import sqlite3

def clear_all_history():
    """Clear all query history from database"""
    conn = sqlite3.connect('../data/court_data.db')
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM queries')
    cursor.execute('DELETE FROM case_data')
    
    conn.commit()
    conn.close()
    print("All search history cleared")

if __name__ == '__main__':
    clear_all_history()