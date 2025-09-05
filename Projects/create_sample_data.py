# create_sample_data.py
import pandas as pd
from datetime import datetime

# Sample books data
books_data = {
    'book_id': [1, 2, 3, 4, 5],
    'title': ['The Alchemist', '1984', 'To Kill a Mockingbird', 'The Great Gatsby', 'Pride and Prejudice'],
    'author': ['Paulo Coelho', 'George Orwell', 'Harper Lee', 'F. Scott Fitzgerald', 'Jane Austen'],
    'copies': [5, 3, 4, 2, 6],
    'description': [
        'A philosophical novel about following one\'s dreams.',
        'A dystopian novel about totalitarianism.',
        'A novel about racial injustice in the American South.',
        'A novel about the American Dream in the 1920s.',
        'A romantic novel about manners and marriage.'
    ],
    'tags': ['adventure, philosophy', 'dystopia, politics', 'drama, social issues', 'classics, romance', 'romance, classics']
}

# Sample transactions data (empty initially)
transactions_data = {
    'transaction_id': [],
    'book_id': [],
    'user_name': [],
    'user_college': [],
    'user_id_email': [],
    'user_phone': [],
    'action': [],  # 'borrow' or 'return'
    'timestamp': []
}

# Create DataFrames
books_df = pd.DataFrame(books_data)
transactions_df = pd.DataFrame(transactions_data)

# Save to Excel
books_df.to_excel('books.xlsx', index=False)
transactions_df.to_excel('transactions.xlsx', index=False)

print("Sample data created successfully.")