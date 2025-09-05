import pandas as pd
from datetime import datetime

# Sample books data with top 10 self-help books for 2025
books_data = {
    'book_id': list(range(1, 11)),
    'title': [
        'Let Them: A Blueprint for Better Boundaries', 
        'Open When: A Practical Guide to Mental Health', 
        'The Power of Ritual', 
        'Attached', 
        'The Upside of Stress', 
        'A Renaissance of Our Own', 
        'The Courage to Be Disliked', 
        'Atomic Habits', 
        'The Subtle Art of Not Giving a F*ck', 
        'Daring Greatly'
    ],
    'author': [
        'Mel Robbins', 
        'Dr. Julie Smith', 
        'Casper ter Kuile', 
        'Amir Levine & Rachel Heller', 
        'Kelly McGonigal', 
        'Rachel Cargle', 
        'Ichiro Kishimi & Fumitake Koga', 
        'James Clear', 
        'Mark Manson', 
        'Brené Brown'
    ],
    'copies': [5, 4, 6, 3, 5, 4, 6, 5, 4, 6],
    'description': [
        'A liberating guide to releasing control over others and embracing personal choice for a fulfilling life.',
        'Practical advice for navigating life’s challenges and improving mental resilience.',
        'Explores how intentional rituals can create deeper meaning and connection in daily life.',
        'A science-based look at attachment styles to build healthier relationships.',
        'Transforms stress into a tool for resilience and growth with a new perspective.',
        'A personal journey of empowerment and challenging societal norms.',
        'Uses Adlerian psychology to guide readers toward happiness and self-worth.',
        'A proven method to build good habits and break bad ones.',
        'A counterintuitive approach to living well by focusing on what truly matters.',
        'A research-based exploration of vulnerability and courage in personal growth.'
    ],
    'tags': [
        'self-help, boundaries', 
        'self-help, mental health', 
        'self-help, mindfulness', 
        'self-help, relationships', 
        'self-help, stress management', 
        'self-help, empowerment', 
        'self-help, psychology', 
        'self-help, habits', 
        'self-help, mindset', 
        'self-help, vulnerability'
    ]
}

# Sample transactions data
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

print("Sample data created successfully with 10 self-help books.")