# 📚 Library Management System – Project Summary

## 🎯 Objective

Build a **Library Management System** using **Python + Streamlit + Excel (for storage)** with **LLM integration** for intelligent query handling.
The system should allow students to:

* Borrow books
* Return books
* View book availability
* Query the library using natural language (via LLM with RAG)

---

## ⚙️ Features

1. **Book Inventory Management (Excel)**

   * Stores list of books with fields: `Book ID, Title, Author, Category, Availability`.
   * Updates availability status (`Available` or `Borrowed`).

2. **Borrowing a Book**

   * User provides: `Name, College ID, Email, Phone, Book ID`.
   * Updates the transaction log.
   * Marks the book as **Borrowed** in inventory.

3. **Returning a Book**

   * User provides: `Book ID`.
   * Updates transaction log with return date.
   * Marks the book as **Available** again.

4. **LLM Query Handling (RAG)**

   * Users can ask:

     * "How many books are available?"
     * "Show me the last 5 borrowed books."
     * "Which books are available in Data Science?"
   * The system retrieves data from Excel and the LLM provides a natural response.

5. **Streamlit Interface**

   * Simple web UI with pages/tabs for:

     * 📖 **Book List**
     * ➕ **Borrow Book**
     * 🔄 **Return Book**
     * 🤖 **Ask Library AI**

---

## 📂 Project Structure

```
library_management_system/
│
├── app.py                  # Main Streamlit app
│
├── data/
│   ├── books.xlsx           # Book inventory
│   └── transactions.xlsx    # Borrow/return records
│
├── modules/
│   ├── book_manager.py      # Handles book add/update/availability
│   ├── transaction_manager.py # Handles borrow/return logging
│   └── rag_engine.py        # Retrieval-Augmented Generation logic
│
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

---

## 📊 Excel File Structures

### `books.xlsx`

| BookID | Title          | Author     | Category    | Availability |
| ------ | -------------- | ---------- | ----------- | ------------ |
| 101    | Python Basics  | John Doe   | Programming | Available    |
| 102    | AI for Finance | Jane Smith | AI          | Borrowed     |

### `transactions.xlsx`

| TransactionID | BookID | BorrowerName | CollegeID | Email                               | Phone      | BorrowDate | ReturnDate |
| ------------- | ------ | ------------ | --------- | ----------------------------------- | ---------- | ---------- | ---------- |
| 1             | 101    | Alex Roy     | CSE123    | [alex@uni.com](mailto:alex@uni.com) | 9876543210 | 2025-09-01 | 2025-09-05 |

---

## 🛠️ Workflow

1. **User visits app** → chooses action (Borrow, Return, Browse, Ask AI).
2. **Borrow flow** → Checks book availability → Logs transaction → Updates Excel.
3. **Return flow** → Logs return date → Updates Excel → Makes book available.
4. **AI Query flow** → Fetches relevant data from Excel → LLM generates human-like response.

