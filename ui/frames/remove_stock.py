"""
Stok Çıkartma Frame
"""

import customtkinter as ctk
from typing import Callable


class RemoveStockFrame(ctk.CTkFrame):
    def __init__(self, parent, database, on_update: Callable = None):
        super().__init__(parent, fg_color="transparent")
        
        self.db = database
        self.on_update = on_update
        self.current_product = None
        self.search_mode = ctk.StringVar(value="barcode")
        
        self._create_widgets()
    
    def _create_widgets(self):
        # Başlık
        title = ctk.CTkLabel(
            self, 
            text="➖ STOK ÇIKART",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(20, 30))
        
        # Arama modu seçimi
        mode_frame = ctk.CTkFrame(self, fg_color="transparent")
        mode_frame.pack(pady=(0, 10))
        
        ctk.CTkLabel(mode_frame, text="Arama Modu:", font=ctk.CTkFont(size=14)).pack(side="left", padx=10)
        
        barcode_radio = ctk.CTkRadioButton(
            mode_frame, 
            text="🏷️ Barkod (Tek Ürün)", 
            variable=self.search_mode, 
            value="barcode",
            font=ctk.CTkFont(size=13),
            command=self._clear_results
        )
        barcode_radio.pack(side="left", padx=10)
        
        product_id_radio = ctk.CTkRadioButton(
            mode_frame, 
            text="📦 Ürün ID (Tüm Bedenler)", 
            variable=self.search_mode, 
            value="product_id",
            font=ctk.CTkFont(size=13),
            command=self._clear_results
        )
        product_id_radio.pack(side="left", padx=10)
        
        # Arama container
        search_frame = ctk.CTkFrame(self, fg_color=("gray90", "gray17"))
        search_frame.pack(fill="x", padx=40, pady=10)
        
        # Arama alanı
        self.search_label = ctk.CTkLabel(
            search_frame, 
            text="🔍 Barkod:", 
            font=ctk.CTkFont(size=14)
        )
        self.search_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        self.search_entry = ctk.CTkEntry(
            search_frame, 
            placeholder_text="Barkodu girin veya okutun...",
            width=300,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.search_entry.grid(row=0, column=1, padx=10, pady=20, sticky="w")
        self.search_entry.bind("<Return>", lambda e: self._search_product())
        
        search_btn = ctk.CTkButton(
            search_frame,
            text="Ara",
            width=80,
            height=40,
            command=self._search_product,
            font=ctk.CTkFont(size=14)
        )
        search_btn.grid(row=0, column=2, padx=20, pady=20)
        
        # Sonuç alanı (scrollable)
        self.result_container = ctk.CTkScrollableFrame(
            self, 
            fg_color=("gray85", "gray20"),
            height=250
        )
        self.result_container.pack(fill="x", padx=40, pady=10)
        
        self.result_placeholder = ctk.CTkLabel(
            self.result_container,
            text="Ürün aramak için barkod veya ürün ID girin...",
            font=ctk.CTkFont(size=16),
            text_color="gray"
        )
        self.result_placeholder.pack(pady=30)
        
        # Mesaj alanı
        self.message_label = ctk.CTkLabel(
            self, 
            text="",
            font=ctk.CTkFont(size=14)
        )
        self.message_label.pack(pady=10)
    
    def _clear_results(self):
        """Sonuçları temizle ve placeholder göster."""
        for widget in self.result_container.winfo_children():
            widget.destroy()
        
        mode = self.search_mode.get()
        if mode == "barcode":
            self.search_label.configure(text="🔍 Barkod:")
            self.search_entry.configure(placeholder_text="Barkodu girin veya okutun...")
            placeholder_text = "Barkod ile arama: Sadece o ürün/beden gösterilir"
        else:
            self.search_label.configure(text="🔍 Ürün ID:")
            self.search_entry.configure(placeholder_text="Ürün ID girin (model kodu)...")
            placeholder_text = "Ürün ID ile arama: Aynı modelin TÜM bedenleri gösterilir"
        
        self.result_placeholder = ctk.CTkLabel(
            self.result_container,
            text=placeholder_text,
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.result_placeholder.pack(pady=30)
        
        self.search_entry.delete(0, "end")
    
    def _search_product(self):
        search_value = self.search_entry.get().strip()
        
        if not search_value:
            self._show_message("❌ Arama değeri girin!", "red")
            return
        
        # Önceki sonuçları temizle
        for widget in self.result_container.winfo_children():
            widget.destroy()
        
        mode = self.search_mode.get()
        
        if mode == "barcode":
            # Barkod ile arama - tek ürün
            product = self.db.search_by_barcode(search_value)
            
            if product:
                self._show_single_product(product)
            else:
                self._show_not_found()
        else:
            # Ürün ID ile arama - tüm bedenler
            products = self.db.search_by_product_id(search_value)
            
            if products:
                self._show_product_group(products)
            else:
                self._show_not_found()
    
    def _show_single_product(self, product):
        """Tek ürün göster (barkod araması)."""
        # id, product_id, barcode, name, size, quantity, price
        card = ctk.CTkFrame(self.result_container, fg_color=("gray80", "gray25"))
        card.pack(fill="x", pady=5, padx=10)
        
        info_text = f"📦 {product[3]} | Beden: {product[4] or '-'} | Stok: {product[5]} | Fiyat: {product[6]:.2f} ₺"
        
        info_label = ctk.CTkLabel(
            card,
            text=info_text,
            font=ctk.CTkFont(size=14)
        )
        info_label.pack(side="left", padx=15, pady=15)
        
        # Çıkartma kontrolleri
        control_frame = ctk.CTkFrame(card, fg_color="transparent")
        control_frame.pack(side="right", padx=10, pady=10)
        
        quantity_entry = ctk.CTkEntry(
            control_frame,
            width=60,
            height=35,
            placeholder_text="1",
            justify="center"
        )
        quantity_entry.pack(side="left", padx=5)
        quantity_entry.insert(0, "1")
        
        remove_btn = ctk.CTkButton(
            control_frame,
            text="📤 Çıkart",
            width=80,
            height=35,
            fg_color=("#C62828", "#B71C1C"),
            hover_color=("#D32F2F", "#C62828"),
            command=lambda p=product, q=quantity_entry: self._remove_stock(p[2], q)
        )
        remove_btn.pack(side="left", padx=5)
    
    def _show_product_group(self, products):
        """Ürün grubu göster (ürün ID araması)."""
        # Özet başlık
        summary = self.db.get_product_summary(products[0][1])
        
        header = ctk.CTkFrame(self.result_container, fg_color=("gray75", "gray30"))
        header.pack(fill="x", pady=(5, 10), padx=10)
        
        header_text = f"📦 {summary['name']} (ID: {summary['product_id']}) | Toplam: {summary['total_quantity']} adet | Değer: {summary['total_value']:.2f} ₺"
        
        ctk.CTkLabel(
            header,
            text=header_text,
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(pady=12, padx=15)
        
        # Her beden için satır
        for product in products:
            # id, product_id, barcode, name, size, quantity, price
            card = ctk.CTkFrame(self.result_container, fg_color=("gray80", "gray25"))
            card.pack(fill="x", pady=3, padx=10)
            
            info_text = f"   {product[4] or '-':^8} | Barkod: {product[2]} | Stok: {product[5]:>4} | Fiyat: {product[6]:.2f} ₺"
            
            info_label = ctk.CTkLabel(
                card,
                text=info_text,
                font=ctk.CTkFont(size=13)
            )
            info_label.pack(side="left", padx=10, pady=12)
            
            # Çıkartma kontrolleri
            control_frame = ctk.CTkFrame(card, fg_color="transparent")
            control_frame.pack(side="right", padx=10, pady=8)
            
            quantity_entry = ctk.CTkEntry(
                control_frame,
                width=50,
                height=30,
                placeholder_text="1",
                justify="center"
            )
            quantity_entry.pack(side="left", padx=3)
            quantity_entry.insert(0, "1")
            
            remove_btn = ctk.CTkButton(
                control_frame,
                text="📤",
                width=40,
                height=30,
                fg_color=("#C62828", "#B71C1C"),
                hover_color=("#D32F2F", "#C62828"),
                command=lambda p=product, q=quantity_entry: self._remove_stock(p[2], q)
            )
            remove_btn.pack(side="left", padx=3)
    
    def _show_not_found(self):
        """Ürün bulunamadı mesajı."""
        label = ctk.CTkLabel(
            self.result_container,
            text="❌ Ürün bulunamadı!",
            font=ctk.CTkFont(size=16),
            text_color="red"
        )
        label.pack(pady=30)
    
    def _remove_stock(self, barcode: str, quantity_entry):
        """Stok çıkart."""
        try:
            quantity = int(quantity_entry.get() or "1")
            if quantity <= 0:
                raise ValueError()
        except ValueError:
            self._show_message("❌ Geçersiz adet!", "red")
            return
        
        success, message = self.db.remove_stock(barcode, quantity)
        
        if success:
            self._show_message(f"✅ {message}", "green")
            # Listeyi yenile
            self._search_product()
            if self.on_update:
                self.on_update()
        else:
            self._show_message(f"❌ {message}", "red")
    
    def _show_message(self, text: str, color: str):
        self.message_label.configure(text=text, text_color=color)
        self.after(3000, lambda: self.message_label.configure(text=""))
    
    def reset(self):
        """Sayfa değiştiğinde çağrılır - formu sıfırla."""
        self._clear_results()
        self.message_label.configure(text="")
