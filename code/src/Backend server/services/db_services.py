import sqlite3
import csv
import pandas as pd
from fastapi.responses import FileResponse

def initialize_db():
    conn = sqlite3.connect('../Database/rules.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    
def get_rules():
    conn = sqlite3.connect('../Database/rules.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rules")
    rules = cursor.fetchall()
    conn.close()
    print(rules)
    return rules

def edit_rules(rule_id, field_name, value):
    conn = sqlite3.connect('../Database/rules.db')
    cursor = conn.cursor()
    cursor.execute(f"UPDATE rules SET {field_name} = ? WHERE id = ?", (value, rule_id))
    conn.commit()
    conn.close()
    return f"Rule with ID {rule_id} updated successfully."

def delete_rules(rule_id): 
    conn = sqlite3.connect('../Database/rules.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM rules WHERE id = ?", (rule_id,))
    conn.commit()
    conn.close()
    return f"Rule with ID {rule_id} deleted successfully."

def add_rules(name, description, status):    
    conn = sqlite3.connect('../Database/rules.db')
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO rules (name, description, status)
            VALUES (?, ?, ?)
        """, (name, description, status))
        conn.commit()
    except sqlite3.OperationalError:
        conn.close()
        initialize_db()
        conn = sqlite3.connect('../Database/rules.db')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO rules (name, description, status)
            VALUES (?, ?, ?)
        """, (name, description, status))
        conn.commit()
    finally:
        conn.close()
    return "New rule added successfully."




def get_transactions():
    conn = sqlite3.connect('../Database/transaction.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions")
    transactions = cursor.fetchall()
    conn.close()
    return transactions

def edit_transactions(transaction_id, field_name, value):
    conn = sqlite3.connect('../Database/transaction.db')
    cursor = conn.cursor()
    cursor.execute(f"UPDATE transactions SET \"{field_name}\" = ? WHERE \"Transaction ID\" = ?", (value, transaction_id))
    conn.commit()
    conn.close()
    return f"Transaction with ID {transaction_id} updated successfully."

def get_transactions_by_id(transaction_id):
    conn = sqlite3.connect('../Database/transaction.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE \"Transaction ID\" = ?", (transaction_id,))
    transaction = cursor.fetchone()
    conn.close()
    return transaction

def update_transactions_from_csv(analysed):
    """
    Updates the transaction database from a CSV file.
    If `analysed` is True, updates from 'analysed_transaction.csv'.
    Otherwise, updates from 'transaction.csv'.
    """
    conn = sqlite3.connect('../Database/transaction.db')
    file_path = '../Temp_files/analysed_transaction.csv' if analysed else '../Temp_files/new_tran.csv'
    table_name = 'analysed_transaction' if analysed else 'transactions'

    try:
        # Read CSV content directly from the file
        df = pd.read_csv(file_path)
        # Set 'Transaction ID' as the index
        df.set_index('Transaction ID', inplace=True)
        # Insert data into the appropriate table
        df.to_sql(table_name, conn, if_exists='replace', index=True)
        return f"{table_name.capitalize()} database updated successfully from CSV."
    except Exception as e:
        return f"Error updating {table_name} from CSV: {str(e)}"
    finally:
        conn.close()

def delete_transactions():
    conn = sqlite3.connect('../Database/transaction.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions")
    conn.commit()
    conn.close()
    return "All transactions deleted successfully."

def get_analysed_transactions():
    conn = sqlite3.connect('../Database/transaction.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analysed_transaction")
    transactions = cursor.fetchall()
    conn.close()
    return transactions

def downloadTransactionCsv():
    file_path = "../Temp_files/analysed_transaction.xlsx"  # Path to the Excel file
    try:
        return FileResponse(file_path, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename="analysed_transaction.xlsx")
    except:
        return {"error": "File processing error, please try again"}