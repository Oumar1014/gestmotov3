import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

class SalesFrame(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        
        # Sales form
        form_frame = ttk.LabelFrame(self, text="Enregistrer une vente", style='Modern.TLabelframe')
        form_frame.pack(padx=10, pady=5, fill='x')
        
        # Grid for form elements
        grid_frame = ttk.Frame(form_frame)
        grid_frame.pack(padx=10, pady=5, fill='x')
        
        # Motorcycle selection
        ttk.Label(grid_frame, text="Moto:", style='Modern.TLabel').grid(row=0, column=0, padx=5, pady=5)
        self.moto_var = tk.StringVar()
        self.moto_combo = ttk.Combobox(grid_frame, textvariable=self.moto_var, style='Modern.TCombobox')
        self.refresh_motos()
        self.moto_combo.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        # Quantity
        ttk.Label(grid_frame, text="Quantité:", style='Modern.TLabel').grid(row=0, column=2, padx=5, pady=5)
        self.qty_var = tk.StringVar()
        ttk.Entry(grid_frame, textvariable=self.qty_var, style='Modern.TEntry').grid(row=0, column=3, padx=5, pady=5, sticky='ew')
        
        # Price
        ttk.Label(grid_frame, text="Prix unitaire:", style='Modern.TLabel').grid(row=0, column=4, padx=5, pady=5)
        self.price_var = tk.StringVar()
        ttk.Entry(grid_frame, textvariable=self.price_var, style='Modern.TEntry').grid(row=0, column=5, padx=5, pady=5, sticky='ew')
        
        # Client Information
        client_frame = ttk.LabelFrame(form_frame, text="Information Client", style='Modern.TLabelframe')
        client_frame.pack(padx=10, pady=5, fill='x')
        
        # Client Name
        ttk.Label(client_frame, text="Nom du Client:", style='Modern.TLabel').grid(row=0, column=0, padx=5, pady=5)
        self.client_name_var = tk.StringVar()
        ttk.Entry(client_frame, textvariable=self.client_name_var, style='Modern.TEntry').grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        # Client Address
        ttk.Label(client_frame, text="Adresse:", style='Modern.TLabel').grid(row=0, column=2, padx=5, pady=5)
        self.client_address_var = tk.StringVar()
        ttk.Entry(client_frame, textvariable=self.client_address_var, style='Modern.TEntry').grid(row=0, column=3, padx=5, pady=5, sticky='ew')
        
        # Client Phone
        ttk.Label(client_frame, text="Téléphone:", style='Modern.TLabel').grid(row=0, column=4, padx=5, pady=5)
        self.client_phone_var = tk.StringVar()
        ttk.Entry(client_frame, textvariable=self.client_phone_var, style='Modern.TEntry').grid(row=0, column=5, padx=5, pady=5, sticky='ew')
        
        # Buttons frame
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.pack(pady=10, fill='x')
        
        # Submit button
        ttk.Button(buttons_frame, text="Enregistrer la vente", 
                  style='Modern.TButton',
                  command=self.record_sale).pack(side=tk.LEFT, padx=5)
        
        # Generate Invoice button
        ttk.Button(buttons_frame, text="Générer Facture", 
                  style='Modern.TButton',
                  command=self.generate_invoice).pack(side=tk.LEFT, padx=5)
        
        # Refresh button
        ttk.Button(buttons_frame, text="Rafraîchir", 
                  style='Modern.TButton',
                  command=self.refresh_motos).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        grid_frame.columnconfigure(1, weight=1)
        grid_frame.columnconfigure(3, weight=1)
        grid_frame.columnconfigure(5, weight=1)
        
        client_frame.columnconfigure(1, weight=1)
        client_frame.columnconfigure(3, weight=1)
        client_frame.columnconfigure(5, weight=1)
    
    def refresh_motos(self):
        inventory = self.db.get_inventory()
        self.moto_combo['values'] = [moto[0] for moto in inventory]
    
    def record_sale(self):
        try:
            name = self.moto_var.get()
            qty = int(self.qty_var.get())
            price = float(self.price_var.get())
            client_name = self.client_name_var.get()
            client_address = self.client_address_var.get()
            client_phone = self.client_phone_var.get()
            
            if not name:
                messagebox.showerror("Erreur", "Veuillez sélectionner une moto!")
                return
            
            if not client_name:
                messagebox.showerror("Erreur", "Veuillez entrer le nom du client!")
                return
            
            if self.db.save_sale(name, qty, price, client_name, client_address, client_phone):
                self.clear_form()
                self.refresh_motos()
                messagebox.showinfo("Succès", "Vente enregistrée avec succès!")
            else:
                messagebox.showerror("Erreur", "Erreur lors de l'enregistrement de la vente!")
        except ValueError:
            messagebox.showerror("Erreur", "Valeurs invalides!")
    
    def clear_form(self):
        self.moto_var.set('')
        self.qty_var.set('')
        self.price_var.set('')
        self.client_name_var.set('')
        self.client_address_var.set('')
        self.client_phone_var.set('')
    
    def generate_invoice(self):
        try:
            name = self.moto_var.get()
            qty = int(self.qty_var.get())
            price = float(self.price_var.get())
            client_name = self.client_name_var.get()
            client_address = self.client_address_var.get()
            client_phone = self.client_phone_var.get()
            
            if not all([name, qty, price, client_name]):
                messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires!")
                return
            
            # Créer le PDF
            filename = f"facture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            c = canvas.Canvas(filename, pagesize=letter)
            
            # En-tête
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, 800, "NOUHOU BAMMA TOURE")
            c.setFont("Helvetica", 10)
            c.drawString(50, 785, "Vendeur des motos")
            c.drawString(50, 770, "Tel : (+223) 77873789 / 90434307 / 83211674")
            c.drawString(50, 755, "Adresse : 5eme Quartier GAO Rep.Du Mali")
            c.drawString(50, 740, "SANILI - KTM")
            c.drawString(50, 725, "NIF : 071003788R - RCCM : Ma.Gao.2013.A.36")
            
            # Informations client
            c.drawString(50, 680, "Information Client:")
            c.drawString(70, 660, f"Nom: {client_name}")
            c.drawString(70, 640, f"Adresse: {client_address}")
            c.drawString(70, 620, f"Téléphone: {client_phone}")
            
            # Détails de la vente
            c.drawString(50, 580, "Détails de la vente:")
            c.drawString(70, 560, f"Moto: {name}")
            c.drawString(70, 540, f"Quantité: {qty}")
            c.drawString(70, 520, f"Prix unitaire: {price:,.2f} FCFA")
            c.drawString(70, 500, f"Total: {qty * price:,.2f} FCFA")
            
            c.save()
            messagebox.showinfo("Succès", f"Facture générée: {filename}")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la génération de la facture: {str(e)}")