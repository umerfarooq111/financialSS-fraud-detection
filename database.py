import sqlite3
import os

DB_FILE = "database.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Allows name-based access to columns
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT UNIQUE NOT NULL,
            sender_name TEXT,
            receiver_name TEXT,
            amount TEXT,
            date_time TEXT,
            scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fraud_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT NOT NULL,
            sender_name TEXT,
            receiver_name TEXT,
            amount TEXT,
            date_time TEXT,
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def check_duplicate(transaction_id):
    """
    Checks if a transaction_id already exists in the database.
    Returns True if it exists, False otherwise.
    """
    if transaction_id == "Not Found":
        return False  # If we couldn't parse the ID, we can't accurately check for duplicates

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM transactions WHERE transaction_id = ?", (transaction_id,))
    result = cursor.fetchone()
    conn.close()
    
    return result is not None

def insert_transaction(data):
    """
    Inserts a new parsed transaction into the database.
    `data` is expected to be a dictionary.
    """
    if data.get("transaction_id") == "Not Found":
        return False # Optionally, we skip inserting transactions that don't have a valid ID

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO transactions (transaction_id, sender_name, receiver_name, amount, date_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data.get("transaction_id"),
            data.get("sender_name"),
            data.get("receiver_name"),
            data.get("amount"),
            data.get("date_time")
        ))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        # This occurs if the transaction_id already exists (since it's UNIQUE)
        success = False
    finally:
        conn.close()
    
    return success

def insert_fraud_transaction(data):
    """
    Inserts a fraud transaction attempt into the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO fraud_transactions (transaction_id, sender_name, receiver_name, amount, date_time)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        data.get("transaction_id"),
        data.get("sender_name"),
        data.get("receiver_name"),
        data.get("amount"),
        data.get("date_time")
    ))
    conn.commit()
    conn.close()

def get_total_transactions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM transactions")
    result = cursor.fetchone()[0]
    conn.close()
    return result

def get_total_income():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT amount FROM transactions")
    amounts = cursor.fetchall()
    conn.close()
    total = 0
    for row in amounts:
        amount_str = row[0]
        if amount_str:
            # Remove currency symbols and commas, assume format like "Rs. 1,000.00"
            clean_amount = amount_str.replace('Rs.', '').replace(',', '').strip()
            try:
                total += float(clean_amount)
            except ValueError:
                pass
    return total

def get_total_fraud_transactions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM fraud_transactions")
    result = cursor.fetchone()[0]
    conn.close()
    return result
