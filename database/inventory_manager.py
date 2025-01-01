"""Gestionnaire de l'inventaire"""
from datetime import datetime, timedelta
import sqlite3

class InventoryManager:
    def __init__(self, db_path):
        self.db_path = db_path

    def get_previous_stock(self, name: str, date: datetime) -> int:
        """Récupère le stock final du jour précédent"""
        previous_date = date - timedelta(days=1)
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT quantity FROM motorcycles 
                    WHERE name = ? AND DATE(created_at) <= DATE(?)
                    ORDER BY created_at DESC LIMIT 1
                """, (name, previous_date.strftime('%Y-%m-%d')))
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            print(f"Erreur lors de la récupération du stock précédent: {e}")
            return 0

    def save_motorcycle(self, name: str, entries: int, price: float, comment: str = "") -> bool:
        """Enregistre ou met à jour une moto dans l'inventaire"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Récupérer les sorties existantes
                cursor.execute("SELECT outputs FROM inventory_movements WHERE motorcycle_id = (SELECT id FROM motorcycles WHERE name = ?)", (name,))
                outputs = cursor.fetchone()
                outputs = outputs[0] if outputs else 0
                
                # Calculer la quantité finale
                final_quantity = entries - outputs
                
                cursor.execute("""
                    INSERT INTO motorcycles (name, quantity, price)
                    VALUES (?, ?, ?)
                    ON CONFLICT(name) DO UPDATE SET
                    quantity = ?,
                    price = ?
                """, (name, final_quantity, price, final_quantity, price))
                
                # Enregistrer le mouvement
                motorcycle_id = cursor.lastrowid or cursor.execute("SELECT id FROM motorcycles WHERE name = ?", (name,)).fetchone()[0]
                cursor.execute("""
                    INSERT INTO inventory_movements (motorcycle_id, entries, outputs, price, comment)
                    VALUES (?, ?, ?, ?, ?)
                """, (motorcycle_id, entries, outputs, price, comment))
                
                return True
        except Exception as e:
            print(f"Erreur lors de l'enregistrement de la moto: {e}")
            return False

    def delete_motorcycle(self, name: str) -> bool:
        """Supprime une moto de l'inventaire"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM motorcycles WHERE name = ?", (name,))
                return True
        except Exception as e:
            print(f"Erreur lors de la suppression de la moto: {e}")
            return False

    def get_inventory(self) -> list:
        """Récupère l'inventaire complet"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT m.name, m.quantity, m.price, 
                           COALESCE(im.entries, 0) as entries,
                           COALESCE(im.outputs, 0) as outputs,
                           COALESCE(im.comment, '') as comment,
                           m.created_at
                    FROM motorcycles m
                    LEFT JOIN inventory_movements im ON m.id = im.motorcycle_id
                """)
                return cursor.fetchall()
        except Exception as e:
            print(f"Erreur lors de la récupération de l'inventaire: {e}")
            return []

    def clear_database(self) -> bool:
        """Nettoie la base de données"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM inventory_movements")
                cursor.execute("DELETE FROM motorcycles")
                return True
        except Exception as e:
            print(f"Erreur lors du nettoyage de la base de données: {e}")
            return False