import pandas as pd
import os

def read_books():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    books_path = os.path.join(script_dir, 'books.xlsx')
    try:
        df = pd.read_excel(books_path)
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=['book_id', 'title', 'author', 'copies', 'description', 'tags'])

def read_transactions():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    transactions_path = os.path.join(script_dir, 'transactions.xlsx')
    try:
        df = pd.read_excel(transactions_path)
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=['transaction_id', 'book_id', 'action', 'user_name', 'user_college', 'user_id_email', 'user_phone', 'timestamp'])

def borrow_book(book_id, user_details):
    books = read_books()
    transactions = read_transactions()
    
    if book_id not in books['book_id'].values or books.loc[books['book_id'] == book_id, 'copies'].iloc[0] <= 0:
        return False, "Book not available or invalid book ID."
    
    new_transaction = pd.DataFrame({
        'transaction_id': [len(transactions) + 1],
        'book_id': [book_id],
        'action': ['borrow'],
        'user_name': [user_details['name']],
        'user_college': [user_details['college']],
        'user_id_email': [user_details['id_email']],
        'user_phone': [user_details['phone']],
        'timestamp': [pd.Timestamp.now().isoformat()]
    })
    
    transactions = pd.concat([transactions, new_transaction], ignore_index=True)
    books.loc[books['book_id'] == book_id, 'copies'] -= 1
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    books_path = os.path.join(script_dir, 'books.xlsx')
    transactions_path = os.path.join(script_dir, 'transactions.xlsx')
    books.to_excel(books_path, index=False)
    transactions.to_excel(transactions_path, index=False)
    
    return True, f"Book {book_id} borrowed successfully by {user_details['name']}."

def return_book(book_id, user_details):
    books = read_books()
    transactions = read_transactions()
    
    if book_id not in books['book_id'].values or books.loc[books['book_id'] == book_id, 'copies'].iloc[0] >= books['copies'].max():
        return False, "Invalid book ID or book not borrowed."
    
    new_transaction = pd.DataFrame({
        'transaction_id': [len(transactions) + 1],
        'book_id': [book_id],
        'action': ['return'],
        'user_name': [user_details['name']],
        'user_college': [user_details['college']],
        'user_id_email': [user_details['id_email']],
        'user_phone': [user_details['phone']],
        'timestamp': [pd.Timestamp.now().isoformat()]
    })
    
    transactions = pd.concat([transactions, new_transaction], ignore_index=True)
    books.loc[books['book_id'] == book_id, 'copies'] += 1
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    books_path = os.path.join(script_dir, 'books.xlsx')
    transactions_path = os.path.join(script_dir, 'transactions.xlsx')
    books.to_excel(books_path, index=False)
    transactions.to_excel(transactions_path, index=False)
    
    return True, f"Book {book_id} returned successfully by {user_details['name']}."

def add_book(book_data):
    books = read_books()
    new_book = pd.DataFrame({
        'book_id': [len(books) + 1],
        'title': [book_data['title']],
        'author': [book_data['author']],
        'copies': [book_data['copies']],
        'description': [book_data['description']],
        'tags': [book_data['tags']]
    })
    books = pd.concat([books, new_book], ignore_index=True)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    books_path = os.path.join(script_dir, 'books.xlsx')
    books.to_excel(books_path, index=False)
    
    return len(books)

def edit_book(book_id, book_data):
    books = read_books()
    if book_id not in books['book_id'].values:
        return False, "Invalid book ID."
    
    for key, value in book_data.items():
        books.loc[books['book_id'] == book_id, key] = value
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    books_path = os.path.join(script_dir, 'books.xlsx')
    books.to_excel(books_path, index=False)
    
    return True, f"Book {book_id} updated successfully."