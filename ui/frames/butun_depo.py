"""
Bütün Depo Frame - Tüm ürünlerin pagination ile görüntülenmesi
Onbinlerce ürün için optimize edilmiş
"""

import customtkinter as ctk
from typing import Callable


class ButunDepoFrame(ctk.CTkFrame):
    def __init__(self, parent, database, on_update: Callable = None):
        super().__init__(parent, fg_color="transparent")
        
        self.db = database
        self.on_update = on_update
        
        # Pagination ayarları
        self.current_page = 1
        self.per_page = 50
        self.total_count = 0
        self.total_pages = 0
        
        self._create_widgets()
    
    def _create_widgets(self):
        # Başlık
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            header, 
            text="📦 BÜTÜN DEPO",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left")
        
        # Sayfa bilgisi
        self.page_info = ctk.CTkLabel(
            header,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.page_info.pack(side="right", padx=10)
        
        # Tablo başlıkları
        headers_frame = ctk.CTkFrame(self, fg_color=("gray80", "gray25"))
        headers_frame.pack(fill="x", padx=20, pady=(10, 0))
        
        headers = [
            ("Ürün ID", 100),
            ("Barkod", 120),
            ("Ürün Adı", 180),
            ("Beden", 60),
            ("Adet", 60),
            ("Fiyat", 80),
            ("Toplam", 90)
        ]
        
        for text, width in headers:
            ctk.CTkLabel(
                headers_frame,
                text=text,
                font=ctk.CTkFont(size=12, weight="bold"),
                width=width
            ).pack(side="left", padx=3, pady=10)
        
        # Scrollable liste
        self.list_container = ctk.CTkScrollableFrame(
            self,
            fg_color=("gray95", "gray17"),
            height=350
        )
        self.list_container.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Pagination kontrolleri
        pagination_frame = ctk.CTkFrame(self, fg_color=("gray85", "gray22"), height=50)
        pagination_frame.pack(fill="x", padx=20, pady=(0, 10))
        pagination_frame.pack_propagate(False)
        
        # Sol taraf - Toplam bilgi
        self.total_info = ctk.CTkLabel(
            pagination_frame,
            text="Toplam: 0 ürün",
            font=ctk.CTkFont(size=13)
        )
        self.total_info.pack(side="left", padx=20, pady=12)
        
        # Sağ taraf - Sayfa kontrolleri
        nav_frame = ctk.CTkFrame(pagination_frame, fg_color="transparent")
        nav_frame.pack(side="right", padx=20)
        
        self.first_btn = ctk.CTkButton(
            nav_frame,
            text="⏮️",
            width=40,
            height=30,
            command=self._first_page
        )
        self.first_btn.pack(side="left", padx=2)
        
        self.prev_btn = ctk.CTkButton(
            nav_frame,
            text="◀",
            width=40,
            height=30,
            command=self._prev_page
        )
        self.prev_btn.pack(side="left", padx=2)
        
        self.page_label = ctk.CTkLabel(
            nav_frame,
            text="1 / 1",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=80
        )
        self.page_label.pack(side="left", padx=10)
        
        self.next_btn = ctk.CTkButton(
            nav_frame,
            text="▶",
            width=40,
            height=30,
            command=self._next_page
        )
        self.next_btn.pack(side="left", padx=2)
        
        self.last_btn = ctk.CTkButton(
            nav_frame,
            text="⏭️",
            width=40,
            height=30,
            command=self._last_page
        )
        self.last_btn.pack(side="left", padx=2)
        
        # Başlangıçta boş mesaj
        self._show_placeholder()
    
    def _show_placeholder(self):
        """Boş mesaj göster."""
        for widget in self.list_container.winfo_children():
            widget.destroy()
        
        self.placeholder = ctk.CTkLabel(
            self.list_container,
            text="📦 Ürünleri görüntülemek için 'Yükle' butonuna tıklayın",
            font=ctk.CTkFont(size=16),
            text_color="gray"
        )
        self.placeholder.pack(pady=80)
        
        load_btn = ctk.CTkButton(
            self.list_container,
            text="📥 Ürünleri Yükle",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            width=150,
            command=self._load_products
        )
        load_btn.pack()
    
    def _load_products(self):
        """Ürünleri yükle."""
        # Temizle
        for widget in self.list_container.winfo_children():
            widget.destroy()
        
        # Verileri al
        products, self.total_count = self.db.get_all_products_paginated(
            self.current_page, 
            self.per_page
        )
        
        if self.total_count == 0:
            label = ctk.CTkLabel(
                self.list_container,
                text="📭 Depoda ürün yok",
                font=ctk.CTkFont(size=16),
                text_color="gray"
            )
            label.pack(pady=80)
            self._update_pagination_info()
            return
        
        # Toplam sayfa hesapla
        self.total_pages = (self.total_count + self.per_page - 1) // self.per_page
        
        # Ürünleri göster
        for product in products:
            self._add_product_row(product)
        
        self._update_pagination_info()
    
    def _add_product_row(self, product):
        """Tek bir ürün satırı ekle."""
        product_id = product[1]
        barcode = product[2]
        name = product[3]
        size = product[4] or "-"
        quantity = product[5]
        price = product[6]
        total = quantity * price
        
        row = ctk.CTkFrame(self.list_container, fg_color=("gray90", "gray20"), height=35)
        row.pack(fill="x", pady=1)
        row.pack_propagate(False)
        
        data = [
            (product_id, 100),
            (barcode, 120),
            (name[:20] + "..." if len(name) > 20 else name, 180),
            (size, 60),
            (str(quantity), 60),
            (f"{price:.2f} ₺", 80),
            (f"{total:.2f} ₺", 90)
        ]
        
        for text, width in data:
            ctk.CTkLabel(
                row,
                text=text,
                font=ctk.CTkFont(size=11),
                width=width,
                anchor="w"
            ).pack(side="left", padx=3, pady=5)
    
    def _update_pagination_info(self):
        """Pagination bilgilerini güncelle."""
        self.total_pages = max(1, (self.total_count + self.per_page - 1) // self.per_page)
        
        self.page_label.configure(text=f"{self.current_page} / {self.total_pages}")
        self.total_info.configure(text=f"Toplam: {self.total_count:,} ürün")
        
        start = (self.current_page - 1) * self.per_page + 1
        end = min(self.current_page * self.per_page, self.total_count)
        
        if self.total_count > 0:
            self.page_info.configure(text=f"Gösterilen: {start}-{end}")
        else:
            self.page_info.configure(text="")
        
        # Buton durumları
        self.first_btn.configure(state="normal" if self.current_page > 1 else "disabled")
        self.prev_btn.configure(state="normal" if self.current_page > 1 else "disabled")
        self.next_btn.configure(state="normal" if self.current_page < self.total_pages else "disabled")
        self.last_btn.configure(state="normal" if self.current_page < self.total_pages else "disabled")
    
    def _first_page(self):
        self.current_page = 1
        self._load_products()
    
    def _prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self._load_products()
    
    def _next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._load_products()
    
    def _last_page(self):
        self.current_page = self.total_pages
        self._load_products()
    
    def refresh(self):
        """Sayfayı yenile."""
        if self.total_count > 0:
            self._load_products()
    
    def reset(self):
        """Sayfa değiştiğinde çağrılır - başlangıç durumuna dön."""
        self.current_page = 1
        self.total_count = 0
        self._show_placeholder()
        self._update_pagination_info()
