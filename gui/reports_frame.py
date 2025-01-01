import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry
from utils.pdf_generator import PDFGenerator

class ReportsFrame(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        
        # Filters frame
        filters_frame = ttk.LabelFrame(self, text="Filtres", style='Modern.TLabelframe')
        filters_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Date filter
        ttk.Label(filters_frame, text="Date:").pack(side=tk.LEFT, padx=5, pady=5)
        self.date_filter = DateEntry(filters_frame, width=12, background='darkblue',
                                   foreground='white', borderwidth=2)
        self.date_filter.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Buttons
        ttk.Button(filters_frame, text="Filtrer", command=self.apply_filter).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(filters_frame, text="Imprimer Rapport", command=self.print_report).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(filters_frame, text="Actualiser", command=self.refresh_report).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Create treeview
        columns = ('Date', 'Moto', 'Client', 'Quantité', 'Prix unitaire', 'Total')
        self.tree = ttk.Treeview(self, columns=columns, show='headings', style='Modern.Treeview')
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # Enable editing
        self.tree.bind('<Double-1>', self.on_double_click)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load initial data
        self.refresh_report()
    
    def on_double_click(self, event):
        """Gérer l'édition directe dans le tableau"""
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            item = self.tree.identify_row(event.y)
            
            # Créer un widget d'édition
            self.edit_cell(item, column)
    
    def edit_cell(self, item, column):
        """Créer un widget d'édition pour la cellule"""
        x, y, w, h = self.tree.bbox(item, column)
        
        # Créer l'entry widget
        entry = ttk.Entry(self.tree, width=20)
        entry.place(x=x, y=y, width=w, height=h)
        
        # Récupérer la valeur actuelle
        current_value = self.tree.set(item, column)
        entry.insert(0, current_value)
        entry.select_range(0, tk.END)
        entry.focus()
        
        def save_edit(event=None):
            """Sauvegarder la modification"""
            new_value = entry.get()
            values = self.tree.item(item)['values']
            sale_id = values[0]  # Assuming first hidden column is ID
            
            try:
                if self.db.update_sale(sale_id, new_value, column):
                    self.tree.set(item, column, new_value)
                    self.refresh_report()
                else:
                    messagebox.showerror("Erreur", "Erreur lors de la mise à jour!")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur: {str(e)}")
            finally:
                entry.destroy()
        
        entry.bind('<Return>', save_edit)
        entry.bind('<Escape>', lambda e: entry.destroy())
    
    def apply_filter(self):
        self.refresh_report()
    
    def print_report(self):
        try:
            selected_date = self.date_filter.get_date()
            sales_data = self.db.get_sales_report(selected_date)
            
            if not sales_data:
                messagebox.showinfo("Info", "Aucune donnée à imprimer pour cette date.")
                return
                
            filename = PDFGenerator.generate_sales_report(selected_date, sales_data)
            messagebox.showinfo("Succès", f"Rapport généré: {filename}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la génération du rapport: {str(e)}")
    
    def refresh_report(self):
        """Rafraîchir l'affichage des ventes"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            selected_date = self.date_filter.get_date()
            sales_data = self.db.get_sales_report(selected_date)
            
            for sale in sales_data:
                self.tree.insert('', 'end', values=(
                    sale['date'],
                    sale['motorcycle'],
                    sale['client'],
                    sale['quantity'],
                    f"{sale['price']:.2f}",
                    f"{sale['total']:.2f}"
                ))
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du rafraîchissement: {str(e)}")