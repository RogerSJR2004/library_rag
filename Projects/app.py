import streamlit as st
from utils import read_books, read_transactions, borrow_book, return_book, add_book, edit_book
from rag import RAG
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

rag = RAG()

# Create tabs for navigation
tabs = st.tabs(["Browse & Borrow", "Return Book", "Admin", "LLM Chat"])

with tabs[0]:
    st.title("Browse & Borrow Books")
    books = read_books()
    st.dataframe(books)
    
    st.subheader("Borrow a Book")
    with st.form("borrow_form"):
        name = st.text_input("Name")
        college = st.text_input("College")
        id_email = st.text_input("ID/Email")
        phone = st.text_input("Phone")
        book_id = st.number_input("Book ID", min_value=1)
        submit = st.form_submit_button("Borrow")
        
        if submit:
            user_details = {'name': name, 'college': college, 'id_email': id_email, 'phone': phone}
            success, message = borrow_book(book_id, user_details)
            if success:
                st.success(message)
                rag.refresh_index()
            else:
                st.error(message)

with tabs[1]:
    st.title("Return Book")
    
    st.subheader("Return a Book")
    with st.form("return_form"):
        name = st.text_input("Name")
        college = st.text_input("College")
        id_email = st.text_input("ID/Email")
        phone = st.text_input("Phone")
        book_id = st.number_input("Book ID", min_value=1)
        submit = st.form_submit_button("Return")
        
        if submit:
            user_details = {'name': name, 'college': college, 'id_email': id_email, 'phone': phone}
            success, message = return_book(book_id, user_details)
            if success:
                st.success(message)
                rag.refresh_index()
            else:
                st.error(message)

with tabs[2]:
    st.title("Admin Panel")
    
    st.subheader("View Books")
    books = read_books()
    st.dataframe(books)
    
    st.subheader("View Latest Transactions")
    transactions = read_transactions().tail(200)
    st.dataframe(transactions)
    
    st.subheader("Add New Book")
    with st.form("add_book_form"):
        title = st.text_input("Title")
        author = st.text_input("Author")
        copies = st.number_input("Copies", min_value=1)
        description = st.text_area("Description")
        tags = st.text_input("Tags (comma-separated)")
        submit_add = st.form_submit_button("Add")
        
        if submit_add:
            book_data = {'title': title, 'author': author, 'copies': copies, 'description': description, 'tags': tags}
            book_id = add_book(book_data)
            st.success(f"Book added with ID {book_id}")
            rag.refresh_index()
    
    st.subheader("Edit Book")
    with st.form("edit_book_form"):
        book_id = st.number_input("Book ID", min_value=1)
        title = st.text_input("New Title (optional)")
        author = st.text_input("New Author (optional)")
        copies = st.number_input("New Copies (optional)", min_value=0)
        description = st.text_area("New Description (optional)")
        tags = st.text_input("New Tags (optional)")
        submit_edit = st.form_submit_button("Edit")
        
        if submit_edit:
            book_data = {}
            if title: book_data['title'] = title
            if author: book_data['author'] = author
            if copies >= 0: book_data['copies'] = copies
            if description: book_data['description'] = description
            if tags: book_data['tags'] = tags
            success, message = edit_book(book_id, book_data)
            if success:
                st.success(message)
                rag.refresh_index()
            else:
                st.error(message)
    
    st.subheader("Export Transactions")
    transactions = read_transactions()
    csv = transactions.to_csv(index=False)
    st.download_button("Download CSV", csv, "transactions.csv", "text/csv")

with tabs[3]:
    st.title("LLM Chat with RAG")
    query = st.text_input("Ask a question about books or transactions")
    if query:
        try:
            context = rag.retrieve(query)
            response = rag.generate(query, context)
            # Split thinking and answer for display
            think_part = response.split("<think>")[1].split("</think>")[0] if "<think>" in response else "No thinking trace available."
            answer_part = response.split("</think>")[-1].strip() if "</think>" in response else response
            # Display answer directly and thinking in a dropdown
            st.write(answer_part)
            with st.expander("View Model's Reasoning Process"):
                st.write(f"<think>{think_part}</think>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}. Please check the terminal for details.")