import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from groq import Groq
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set. Please configure it in your environment.")
client = Groq(api_key=GROQ_API_KEY)
MODEL = "deepseek-r1-distill-llama-70b"  
embedder = SentenceTransformer('all-MiniLM-L6-v2')  # Hugging Face embeddings

class RAG:
    def __init__(self):
        self.books_index = None
        self.transactions_index = None
        self.books_df = None
        self.transactions_df = None
        self.refresh_index()

    def refresh_index(self):
        # Use os.path.join to construct paths relative to the script location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        books_path = os.path.join(script_dir, 'books.xlsx')
        transactions_path = os.path.join(script_dir, 'transactions.xlsx')
        
        self.books_df = pd.read_excel(books_path)
        self.transactions_df = pd.read_excel(transactions_path)
        
        books_texts = self.books_df.apply(
            lambda row: f"Book ID: {row['book_id']}, Title: {row['title']}, Author: {row['author']}, Description: {row['description']}, Tags: {row['tags']}, Copies Available: {row['copies']} (available if copies > 0, out of stock if copies = 0)", 
            axis=1
        )
        books_embeddings = embedder.encode(books_texts)
        
        dim = books_embeddings.shape[1]
        self.books_index = faiss.IndexFlatL2(dim)
        self.books_index.add(books_embeddings.astype(np.float32))
        
        self.book_id_to_index = {row['book_id']: idx for idx, row in self.books_df.iterrows()}
        self.index_to_book_id = {idx: row['book_id'] for idx, row in self.books_df.iterrows()}
        
        if not self.transactions_df.empty:
            transactions_texts = self.transactions_df.apply(
                lambda row: f"Transaction ID: {row['transaction_id']}, Book ID: {row['book_id']}, Action: {row['action']}, User: {row['user_name']}, College: {row['user_college']}, ID/Email: {row['user_id_email']}, Phone: {row['user_phone']}, Timestamp: {row['timestamp']}", 
                axis=1
            )
            transactions_embeddings = embedder.encode(transactions_texts)
            self.transactions_index = faiss.IndexFlatL2(dim)
            self.transactions_index.add(transactions_embeddings.astype(np.float32))
        else:
            self.transactions_index = faiss.IndexFlatL2(dim)

    def retrieve(self, query, top_k=5):
        query_emb = embedder.encode([query])
        
        _, books_indices = self.books_index.search(query_emb.astype(np.float32), top_k)
        book_ids = [self.index_to_book_id.get(idx, None) for idx in books_indices[0]]
        books_retrieved = self.books_df[self.books_df['book_id'].isin(book_ids)]
        books_context = books_retrieved.to_string(index=False)
        
        if self.transactions_index.ntotal > 0:
            _, trans_indices = self.transactions_index.search(query_emb.astype(np.float32), top_k)
            trans_retrieved = self.transactions_df.iloc[trans_indices[0]].to_string(index=False)
        else:
            trans_retrieved = "No transactions available."
        
        insights = self.generate_insights()
        
        return f"Books (real-time data):\n{books_context}\n\nTransactions:\n{trans_retrieved}\n\nInsights:\n{insights}"

    def generate_insights(self):
        insights = []
        
        if not self.transactions_df.empty:
            borrow_counts = self.transactions_df[self.transactions_df['action'] == 'borrow']['book_id'].value_counts()
            if not borrow_counts.empty:
                top_book_id = borrow_counts.index[0]
                top_book = self.books_df[self.books_df['book_id'] == top_book_id][['title', 'author', 'copies']].iloc[0]
                availability = f"available with {top_book['copies']} copies" if top_book['copies'] > 0 else "out of stock"
                insights.append(f"Most borrowed book: '{top_book['title']}' by {top_book['author']} (Borrowed {borrow_counts.iloc[0]} times, currently {availability})")
        
        low_stock = self.books_df[self.books_df['copies'] <= 1]
        if not low_stock.empty:
            low_stock_info = []
            for _, row in low_stock.iterrows():
                status = "out of stock" if row['copies'] == 0 else f"low stock (only {row['copies']} copy left)"
                low_stock_info.append(f"'{row['title']}' by {row['author']} ({status})")
            insights.append(f"Books with low availability: {', '.join(low_stock_info)}")
        
        if not self.transactions_df.empty:
            one_week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            recent_trans = self.transactions_df[self.transactions_df['timestamp'] >= one_week_ago]
            if not recent_trans.empty:
                borrow_count = len(recent_trans[recent_trans['action'] == 'borrow'])
                return_count = len(recent_trans[recent_trans['action'] == 'return'])
                insights.append(f"Last 7 days: {borrow_count} books borrowed, {return_count} books returned")
        
        return "\n".join(insights) if insights else "No insights available at this time."

    def generate(self, query, context):
        prompt = f"""Context (real-time data from library system):
{context}

Query: {query}

Instructions:
- You are a library assistant. Include your reasoning process in a single <think> block before the final answer, and do not include the answer within the <think> block. The <think> block should only contain your step-by-step reasoning process.
- For availability: A book is available if 'Copies Available' > 0 (report the exact number, e.g., 'available with 3 copies remaining'). It is out of stock only if copies = 0.
- If the query asks about a specific book ID, use the 'Book ID' field to identify it, then report title, author, description, tags, and availability.
- For general queries (e.g., 'available books' or 'books in AI'), list relevant books with titles, authors, tags, and availability status/copies.
- For transaction queries, summarize details (e.g., who borrowed/returned, when) and link to current availability.
- Use insights to add value, such as trends, low stock warnings, or recommendations.
- Format the final answer (outside the <think> block) clearly with bullet points or paragraphs for readability.
- If no relevant information, say so politely.
"""

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful and insightful library assistant capable of reasoning through queries."},
                {"role": "user", "content": prompt}
            ],
            model=MODEL,
        )
        
        response = chat_completion.choices[0].message.content
        # Parse thinking and answer
        think_part = ""
        answer_part = response
        if "<think>" in response and "</think>" in response:
            parts = response.split("</think>")
            think_part = parts[0].replace("<think>", "<think>").strip()
            answer_part = parts[1].strip() if len(parts) > 1 else "No final answer generated."
        else:
            think_part = "<think> The model did not provide a detailed reasoning process. </think>"
        
        return f"{think_part}\n{answer_part}"