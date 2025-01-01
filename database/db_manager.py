import sqlite3
from datetime import datetime
from pathlib import Path

class DatabaseManager:
    def __init__(self):
        self.db_path = Path('inventory.db')
        self.init_database()
    
    def init_database(self):
        """Initialize database with schema"""
        with open('database/schema.sql', 'r') as f:
            schema = f.read()
            
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(schema)
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    def save_motorcycle(self, name: str, quantity: int, price: float) -> bool:
        """Save or update motorcycle in database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO motorcycles (name, quantity, price)
                    VALUES (?, ?, ?)
                    ON CONFLICT(name) DO UPDATE SET
                    quantity = ?,
                    price = ?
                """, (name, quantity, price, quantity, price))
                return True
        except Exception as e:
            print(f"Error saving motorcycle: {e}")
            return False

    def save_sale(self, motorcycle_name: str, quantity: int, price: float,
                 client_name: str, client_address: str, client_phone: str) -> bool:
        """Record a sale in database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get motorcycle id
                cursor.execute("SELECT id FROM motorcycles WHERE name = ?", (motorcycle_name,))
                motorcycle_id = cursor.fetchone()[0]
                
                # Record sale
                cursor.execute("""
                    INSERT INTO sales (motorcycle_id, quantity, price, client_name, 
                                     client_address, client_phone)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (motorcycle_id, quantity, price, client_name, client_address, client_phone))
                
                # Update motorcycle quantity
                cursor.execute("""
                    UPDATE motorcycles 
                    SET quantity = quantity - ?
                    WHERE id = ?
                """, (quantity, motorcycle_id))
                
                return True
        except Exception as e:
            print(f"Error recording sale: {e}")
            return False

    def update_sale(self, sale_id: int, quantity: int, price: float,
                   client_name: str) -> bool:
        """Update existing sale"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE sales 
                    SET quantity = ?, price = ?, client_name = ?
                    WHERE id = ?
                """, (quantity, price, client_name, sale_id))
                return True
        except Exception as e:
            print(f"Error updating sale: {e}")
            return False

    def get_sales_report(self, date: datetime = None) -> list:
        """Get sales report for specific date"""
        query = """
            SELECT s.id, s.sale_date, m.name, s.client_name, 
                   s.quantity, s.price, (s.quantity * s.price) as total
            FROM sales s
            JOIN motorcycles m ON s.motorcycle_id = m.id
        """
        params = []
        
        if date:
            query += " WHERE DATE(s.sale_date) = DATE(?)"
            params.append(date.isoformat())
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting sales report: {e}")
            return []

    def get_inventory(self) -> list:
        """Get current inventory"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name, quantity, price FROM motorcycles")
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting inventory: {e}")
            return []