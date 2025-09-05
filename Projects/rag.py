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
client = Groq(api_key=GROQ_API_KEY)
MODEL = "deepseek-r1-distill-llama-70b"  # Updated model as provided
embedder = SentenceTransformer('all-MiniLM-L6-v2')  # Hugging Face embeddings

class RAG:
    def __init__(self):
        self.books_index = None
        self.transactions_index = None
        self.books_df = None
        self.transactions_df = None
        self.refresh_index()

    def refresh_index(self):
        # Load books and transactions
        self.books_df = pd.read_excel('books.xlsx')
        self.transactions_df = pd.read_excel('transactions.xlsx')
        
        # Embed books: combine title, author, description, tags
        books_texts = self.books_df.apply(
            lambda row: f"Book ID: {row['book_id']}, Title: {row['title']}, Author: {row['author']}, Description: {row['description']}, Tags: {row['tags']}, Copies Available: {row['copies']}", 
            axis=1
        )
        books_embeddings = embedder.encode(books_texts)
        
        # Initialize books FAISS index
        dim = books_embeddings.shape[1]
        self.books_index = faiss.IndexFlatL2(dim)
        self.books_index.add(books_embeddings.astype(np.float32))
        
        # Store book_id to index mapping
        self.book_id_to_index = {row['book_id']: idx for idx, row in self.books_df.iterrows()}
        self.index_to_book_id = {idx: row['book_id'] for idx, row in self.books_df.iterrows()}
        
        # Handle transactions: only embed if not empty
        if not self.transactions_df.empty:
            transactions_texts = self.transactions_df.apply(
                lambda row: f"Transaction ID: {row['transaction_id']}, Book ID: {row['book_id']}, Action: {row['action']}, User: {row['user_name']}, College: {row['user_college']}, ID/Email: {row['user_id_email']}, Phone: {row['user_phone']}, Timestamp: {row['timestamp']}", 
                axis=1
            )
            transactions_embeddings = embedder.encode(transactions_texts)
            self.transactions_index = faiss.IndexFlatL2(dim)
            self.transactions_index.add(transactions_embeddings.astype(np.float32))
        else:
            # Initialize an empty FAISS index for transactions
            self.transactions_index = faiss.IndexFlatL2(dim)

    def retrieve(self, query, top_k=5):
        query_emb = embedder.encode([query])
        
        # Retrieve from books
        _, books_indices = self.books_index.search(query_emb.astype(np.float32), top_k)
        # Map FAISS indices to book_id
        book_ids = [self.index_to_book_id.get(idx, None) for idx in books_indices[0]]
        books_retrieved = self.books_df[self.books_df['book_id'].isin(book_ids)]
        books_context = books_retrieved.to_string(index=False)
        
        # Retrieve from transactions (handle empty index)
        if self.transactions_index.ntotal > 0:
            _, trans_indices = self.transactions_index.search(query_emb.astype(np.float32), top_k)
            trans_retrieved = self.transactions_df.iloc[trans_indices[0]].to_string(index=False)
        else:
            trans_retrieved = "No transactions available."
        
        # Generate insights for admins/users
        insights = self.generate_insights()
        
        return f"Books:\n{books_context}\n\nTransactions:\n{trans_retrieved}\n\nInsights:\n{insights}"

    def generate_insights(self):
        insights = []
        
        # Insight 1: Most borrowed books
        if not self.transactions_df.empty:
            borrow_counts = self.transactions_df[self.transactions_df['action'] == 'borrow']['book_id'].value_counts()
            if not borrow_counts.empty:
                top_book_id = borrow_counts.index[0]
                top_book = self.books_df[self.books_df['book_id'] == top_book_id][['title', 'author']].iloc[0]
                insights.append(f"Most borrowed book: '{top_book['title']}' by {top_book['author']} (Borrowed {borrow_counts.iloc[0]} times)")
        
        # Insight 2: Books with low availability
        low_stock = self.books_df[self.books_df['copies'] <= 1]
        if not low_stock.empty:
            low_stock_titles = low_stock['title'].tolist()
            insights.append(f"Books with low stock (<= 1 copy): {', '.join(low_stock_titles)}")
        
        # Insight 3: Recent activity summary
        if not self.transactions_df.empty:
            one_week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            recent_trans = self.transactions_df[self.transactions_df['timestamp'] >= one_week_ago]
            if not recent_trans.empty:
                borrow_count = len(recent_trans[recent_trans['action'] == 'borrow'])
                return_count = len(recent_trans[recent_trans['action'] == 'return'])
                insights.append(f"Last 7 days: {borrow_count} books borrowed, {return_count} books returned")
        
        return "\n".join(insights) if insights else "No insights available at this time."

    def generate(self, query, context):
        prompt = f"""Context:
{context}

Query: {query}

Instructions:
- You are a library assistant. Answer the query concisely and accurately based only on the provided context.
- If the query asks about a specific book ID, use the 'Book ID' field in the context to identify the correct book.
- For general queries (e.g., 'available books'), list relevant books with their titles, authors, and available copies.
- For transaction queries, summarize relevant transaction details (e.g., who borrowed, when).
- Use insights to provide additional value, such as trends or recommendations.
- Format the response clearly with bullet points or paragraphs for readability.
- If no relevant information is found, say so politely.
"""
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful and insightful library assistant."},
                {"role": "user", "content": prompt}
            ],
            model=MODEL,
        )
        
        return chat_completion.choices[0].message.content