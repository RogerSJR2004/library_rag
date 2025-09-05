# utils.py
import pandas as pd
from datetime import datetime
import os

def read_books():
    if os.path.exists('books.xlsx'):
        return pd.read_excel('books.xlsx')
    else:
        return pd.DataFrame(columns=['book_id', 'title', 'author', 'copies', 'description', 'tags'])

def write_books(df):
    df.to_excel('books.xlsx', index=False)

def read_transactions():
    if os.path.exists('transactions.xlsx'):
        return pd.read_excel('transactions.xlsx')
    else:
        return pd.DataFrame(columns=['transaction_id', 'book_id', 'user_name', 'user_college', 'user_id_email', 'user_phone', 'action', 'timestamp'])

def write_transactions(df):
    df.to_excel('transactions.xlsx', index=False)

def borrow_book(book_id, user_details):
    books = read_books()
    transactions = read_transactions()
    
    book = books[books['book_id'] == book_id]
    if book.empty or book['copies'].values[0] <= 0:
        return False, "Book not available."
    
    # Update copies
    books.loc[books['book_id'] == book_id, 'copies'] -= 1
    write_books(books)
    
    # Log transaction
    transaction_id = len(transactions) + 1
    new_transaction = {
        'transaction_id': transaction_id,
        'book_id': book_id,
        'user_name': user_details['name'],
        'user_college': user_details['college'],
        'user_id_email': user_details['id_email'],
        'user_phone': user_details['phone'],
        'action': 'borrow',
        'timestamp': datetime.now().isoformat()
    }
    transactions = pd.concat([transactions, pd.DataFrame([new_transaction])], ignore_index=True)
    write_transactions(transactions)
    
    return True, "Book borrowed successfully."

def return_book(book_id, user_details):
    books = read_books()
    transactions = read_transactions()
    
    book = books[books['book_id'] == book_id]
    if book.empty:
        return False, "Book not found."
    
    # Update copies
    books.loc[books['book_id'] == book_id, 'copies'] += 1
    write_books(books)
    
    # Log transaction
    transaction_id = len(transactions) + 1
    new_transaction = {
        'transaction_id': transaction_id,
        'book_id': book_id,
        'user_name': user_details['name'],
        'user_college': user_details['college'],
        'user_id_email': user_details['id_email'],
        'user_phone': user_details['phone'],
        'action': 'return',
        'timestamp': datetime.now().isoformat()
    }
    transactions = pd.concat([transactions, pd.DataFrame([new_transaction])], ignore_index=True)
    write_transactions(transactions)
    
    return True, "Book returned successfully."

def add_book(book_data):
    books = read_books()
    book_id = books['book_id'].max() + 1 if not books.empty else 1
    new_book = {
        'book_id': book_id,
        'title': book_data['title'],
        'author': book_data['author'],
        'copies': book_data['copies'],
        'description': book_data['description'],
        'tags': book_data['tags']
    }
    books = pd.concat([books, pd.DataFrame([new_book])], ignore_index=True)
    write_books(books)
    return book_id

def edit_book(book_id, book_data):
    books = read_books()
    if book_id not in books['book_id'].values:
        return False, "Book not found."
    for key, value in book_data.items():
        books.loc[books['book_id'] == book_id, key] = value
    write_books(books)
    return True, "Book updated successfully."