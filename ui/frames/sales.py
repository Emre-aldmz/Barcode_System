"""
Satış Arayüzü Frame (POS - Point of Sale)
Ana sayfa - Barkod okutma ve satış işlemleri
"""

import customtkinter as ctk
from typing import Callable, Dict, List
from datetime import datetime


class SalesFrame(ctk.CTkFrame):
    def __init__(self, parent, database, on_update: Callable = None):
        super().__init__(parent, fg_color="transparent")
        
        self.db = database
        self.on_update = on_update
        
        # Sepet: {barcode: {product_info, quantity}}
        self.cart: Dict[str, dict] = {}
        
        # Ödeme yöntemi (başlangıçta seçili değil)
        self.payment_method = ctk.StringVar(value="")
        self.cash_selected = ctk.BooleanVar(value=False)
        self.card_selected = ctk.BooleanVar(value=False)
        
        self._create_widgets()
    
    def _create_widgets(self):
        # Ana container - 2 sütunlu layout
        self.grid_columnconfigure(0, weight=2)  # Sol taraf (sepet)
        self.grid_columnconfigure(1, weight=1)  # Sağ taraf (özet)
        self.grid_rowconfigure(1, weight=1)
        
        # ===== BAŞLIK =====
        header = ctk.CTkFrame(self, fg_color=("gray85", "gray20"), height=70)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))
        header.grid_propagate(False)
        
        title = ctk.CTkLabel(
            header,
            text="🛒 SATIŞ",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(side="left", padx=20, pady=15)
        
        # Barkod giriş alanı
        barcode_frame = ctk.CTkFrame(header, fg_color="transparent")
        barcode_frame.pack(side="left", padx=30, pady=10)
        
        ctk.CTkLabel(
            barcode_frame,
            text="🔍",
            font=ctk.CTkFont(size=20)
        ).pack(side="left", padx=5)
        
        self.barcode_entry = ctk.CTkEntry(
            barcode_frame,
            placeholder_text="Barkod okutun veya girin...",
            width=300,
            height=45,
            font=ctk.CTkFont(size=16)
        )
        self.barcode_entry.pack(side="left", padx=5)
        self.barcode_entry.bind("<Return>", lambda e: self._add_to_cart())
        
        add_btn = ctk.CTkButton(
            barcode_frame,
            text="EKLE",
            width=80,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._add_to_cart
        )
        add_btn.pack(side="left", padx=5)
        
        # Tarih/saat
        self.datetime_label = ctk.CTkLabel(
            header,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.datetime_label.pack(side="right", padx=20)
        self._update_datetime()
        
        # ===== SOL TARAF - SEPET =====
        cart_container = ctk.CTkFrame(self, fg_color=("gray90", "gray17"))
        cart_container.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=5)
        
        cart_header = ctk.CTkFrame(cart_container, fg_color=("gray80", "gray25"), height=40)
        cart_header.pack(fill="x")
        cart_header.pack_propagate(False)
        
        headers = [("Ürün", 200), ("Beden", 60), ("Adet", 60), ("Birim", 80), ("Toplam", 90), ("", 40)]
        for text, width in headers:
            ctk.CTkLabel(
                cart_header,
                text=text,
                font=ctk.CTkFont(size=12, weight="bold"),
                width=width
            ).pack(side="left", padx=5, pady=10)
        
        self.cart_list = ctk.CTkScrollableFrame(
            cart_container,
            fg_color="transparent"
        )
        self.cart_list.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Boş sepet mesajı
        self.empty_cart_label = ctk.CTkLabel(
            self.cart_list,
            text="🛒 Sepet boş\nBarkod okutarak ürün ekleyin",
            font=ctk.CTkFont(size=18),
            text_color="gray"
        )
        self.empty_cart_label.pack(pady=100)
        
        # ===== SAĞ TARAF - ÖZET =====
        summary_container = ctk.CTkFrame(self, fg_color=("gray85", "gray20"))
        summary_container.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=5)
        
        # Özet başlık
        ctk.CTkLabel(
            summary_container,
            text="📋 ÖZET",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=15)
        
        # Özet bilgiler
        summary_info = ctk.CTkFrame(summary_container, fg_color="transparent")
        summary_info.pack(fill="x", padx=20, pady=10)
        
        # Ürün sayısı
        items_row = ctk.CTkFrame(summary_info, fg_color="transparent")
        items_row.pack(fill="x", pady=5)
        ctk.CTkLabel(items_row, text="Ürün Çeşidi:", font=ctk.CTkFont(size=14)).pack(side="left")
        self.items_count_label = ctk.CTkLabel(items_row, text="0", font=ctk.CTkFont(size=14, weight="bold"))
        self.items_count_label.pack(side="right")
        
        # Toplam adet
        qty_row = ctk.CTkFrame(summary_info, fg_color="transparent")
        qty_row.pack(fill="x", pady=5)
        ctk.CTkLabel(qty_row, text="Toplam Adet:", font=ctk.CTkFont(size=14)).pack(side="left")
        self.total_qty_label = ctk.CTkLabel(qty_row, text="0", font=ctk.CTkFont(size=14, weight="bold"))
        self.total_qty_label.pack(side="right")
        
        # Ayraç
        ctk.CTkFrame(summary_container, fg_color="gray50", height=2).pack(fill="x", padx=20, pady=10)
        
        # TOPLAM
        total_frame = ctk.CTkFrame(summary_container, fg_color=("gray75", "gray30"))
        total_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            total_frame,
            text="TOPLAM",
            font=ctk.CTkFont(size=16)
        ).pack(side="left", padx=15, pady=15)
        
        self.total_price_label = ctk.CTkLabel(
            total_frame,
            text="0.00 ₺",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("#1B5E20", "#4CAF50")
        )
        self.total_price_label.pack(side="right", padx=15, pady=15)
        
        # ===== ÖDEME YÖNTEMİ =====
        payment_frame = ctk.CTkFrame(summary_container, fg_color="transparent")
        payment_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            payment_frame,
            text="Ödeme Yöntemi:",
            font=ctk.CTkFont(size=13)
        ).pack(pady=(0, 10))
        
        payment_buttons = ctk.CTkFrame(payment_frame, fg_color="transparent")
        payment_buttons.pack()
        
        # Kare checkbox'lar (sadece biri seçilebilir)
        self.cash_checkbox = ctk.CTkCheckBox(
            payment_buttons,
            text="💵 NAKİT",
            variable=self.cash_selected,
            font=ctk.CTkFont(size=14, weight="bold"),
            checkbox_width=24,
            checkbox_height=24,
            corner_radius=4,
            command=self._on_cash_selected
        )
        self.cash_checkbox.pack(side="left", padx=15)
        
        self.card_checkbox = ctk.CTkCheckBox(
            payment_buttons,
            text="💳 KREDİ KARTI",
            variable=self.card_selected,
            font=ctk.CTkFont(size=14, weight="bold"),
            checkbox_width=24,
            checkbox_height=24,
            corner_radius=4,
            command=self._on_card_selected
        )
        self.card_checkbox.pack(side="left", padx=15)
        
        # Butonlar
        btn_frame = ctk.CTkFrame(summary_container, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=15)
        
        self.complete_btn = ctk.CTkButton(
            btn_frame,
            text="✅ SATIŞI TAMAMLA",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            fg_color=("#2E7D32", "#1B5E20"),
            hover_color=("#388E3C", "#2E7D32"),
            command=self._complete_sale,
            state="disabled"
        )
        self.complete_btn.pack(fill="x", pady=5)
        
        self.clear_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️ SEPETİ TEMİZLE",
            font=ctk.CTkFont(size=14),
            height=40,
            fg_color=("#C62828", "#B71C1C"),
            hover_color=("#D32F2F", "#C62828"),
            command=self._clear_cart
        )
        self.clear_btn.pack(fill="x", pady=5)
        
        # Mesaj alanı
        self.message_label = ctk.CTkLabel(
            summary_container,
            text="",
            font=ctk.CTkFont(size=13),
            wraplength=200
        )
        self.message_label.pack(pady=10)
    
    def _update_datetime(self):
        """Tarih/saat güncelle."""
        now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        self.datetime_label.configure(text=now)
        self.after(1000, self._update_datetime)
    
    def _add_to_cart(self):
        """Barkod ile ürünü sepete ekle."""
        barcode = self.barcode_entry.get().strip()
        
        if not barcode:
            return
        
        product = self.db.search_by_barcode(barcode)
        
        if not product:
            self._show_message("❌ Ürün bulunamadı!", "red")
            self.barcode_entry.delete(0, "end")
            return
        
        stock_qty = product[5]
        current_cart_qty = self.cart.get(barcode, {}).get('quantity', 0)
        
        if current_cart_qty >= stock_qty:
            self._show_message(f"❌ Yetersiz stok! Mevcut: {stock_qty}", "red")
            self.barcode_entry.delete(0, "end")
            return
        
        if barcode in self.cart:
            self.cart[barcode]['quantity'] += 1
        else:
            self.cart[barcode] = {
                'id': product[0],
                'product_id': product[1],
                'barcode': product[2],
                'name': product[3],
                'size': product[4] or '-',
                'price': product[6],
                'stock': stock_qty,
                'quantity': 1
            }
        
        self._show_message(f"✅ {product[3]} eklendi", "green")
        self.barcode_entry.delete(0, "end")
        self.barcode_entry.focus()
        
        self._refresh_cart()
    
    def _refresh_cart(self):
        """Sepet görünümünü yenile."""
        for widget in self.cart_list.winfo_children():
            widget.destroy()
        
        if not self.cart:
            self.empty_cart_label = ctk.CTkLabel(
                self.cart_list,
                text="🛒 Sepet boş\nBarkod okutarak ürün ekleyin",
                font=ctk.CTkFont(size=18),
                text_color="gray"
            )
            self.empty_cart_label.pack(pady=100)
            self.complete_btn.configure(state="disabled")
            self._update_summary()
            return
        
        self.complete_btn.configure(state="normal")
        
        for barcode, item in self.cart.items():
            row = ctk.CTkFrame(self.cart_list, fg_color=("gray85", "gray22"), height=45)
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)
            
            ctk.CTkLabel(
                row,
                text=item['name'][:25],
                font=ctk.CTkFont(size=12),
                width=200,
                anchor="w"
            ).pack(side="left", padx=5, pady=8)
            
            ctk.CTkLabel(
                row,
                text=item['size'],
                font=ctk.CTkFont(size=12),
                width=60
            ).pack(side="left", padx=5)
            
            qty_frame = ctk.CTkFrame(row, fg_color="transparent", width=60)
            qty_frame.pack(side="left", padx=5)
            qty_frame.pack_propagate(False)
            
            ctk.CTkButton(
                qty_frame,
                text="-",
                width=20,
                height=25,
                command=lambda b=barcode: self._change_quantity(b, -1)
            ).pack(side="left")
            
            ctk.CTkLabel(
                qty_frame,
                text=str(item['quantity']),
                font=ctk.CTkFont(size=12, weight="bold"),
                width=20
            ).pack(side="left", padx=2)
            
            ctk.CTkButton(
                qty_frame,
                text="+",
                width=20,
                height=25,
                command=lambda b=barcode: self._change_quantity(b, 1)
            ).pack(side="left")
            
            ctk.CTkLabel(
                row,
                text=f"{item['price']:.2f} ₺",
                font=ctk.CTkFont(size=12),
                width=80
            ).pack(side="left", padx=5)
            
            line_total = item['price'] * item['quantity']
            ctk.CTkLabel(
                row,
                text=f"{line_total:.2f} ₺",
                font=ctk.CTkFont(size=12, weight="bold"),
                width=90
            ).pack(side="left", padx=5)
            
            ctk.CTkButton(
                row,
                text="✕",
                width=30,
                height=25,
                fg_color=("#E53935", "#C62828"),
                hover_color=("#F44336", "#E53935"),
                command=lambda b=barcode: self._remove_from_cart(b)
            ).pack(side="left", padx=5)
        
        self._update_summary()
    
    def _change_quantity(self, barcode: str, delta: int):
        """Adet değiştir."""
        if barcode not in self.cart:
            return
        
        new_qty = self.cart[barcode]['quantity'] + delta
        
        if new_qty <= 0:
            self._remove_from_cart(barcode)
            return
        
        if new_qty > self.cart[barcode]['stock']:
            self._show_message(f"❌ Yetersiz stok! Max: {self.cart[barcode]['stock']}", "red")
            return
        
        self.cart[barcode]['quantity'] = new_qty
        self._refresh_cart()
    
    def _remove_from_cart(self, barcode: str):
        """Ürünü sepetten çıkar."""
        if barcode in self.cart:
            del self.cart[barcode]
            self._refresh_cart()
    
    def _update_summary(self):
        """Özet bilgileri güncelle."""
        item_count = len(self.cart)
        total_qty = sum(item['quantity'] for item in self.cart.values())
        total_price = sum(item['price'] * item['quantity'] for item in self.cart.values())
        
        self.items_count_label.configure(text=str(item_count))
        self.total_qty_label.configure(text=str(total_qty))
        self.total_price_label.configure(text=f"{total_price:,.2f} ₺")
    
    def _on_cash_selected(self):
        """Nakit seçildiğinde kredi kartını kaldır."""
        if self.cash_selected.get():
            self.card_selected.set(False)
            self.payment_method.set("cash")
        else:
            self.payment_method.set("")
    
    def _on_card_selected(self):
        """Kredi kartı seçildiğinde nakiti kaldır."""
        if self.card_selected.get():
            self.cash_selected.set(False)
            self.payment_method.set("card")
        else:
            self.payment_method.set("")
    
    def _complete_sale(self):
        """Satışı tamamla - stoktan düş ve kaydet."""
        if not self.cart:
            return
        
        # Ödeme yöntemi kontrolü
        payment_method = self.payment_method.get()
        if not payment_method:
            self._show_message("❌ Ödeme yöntemi seçin!", "red")
            return
        
        total = sum(item['price'] * item['quantity'] for item in self.cart.values())
        
        # Satış kaydı için item listesi
        items_for_record = []
        
        # Stokları düş
        errors = []
        for barcode, item in self.cart.items():
            success, msg = self.db.remove_stock(barcode, item['quantity'])
            if not success:
                errors.append(f"{item['name']}: {msg}")
            else:
                items_for_record.append({
                    'barcode': barcode,
                    'name': item['name'],
                    'size': item['size'],
                    'quantity': item['quantity'],
                    'price': item['price'],
                    'total': item['price'] * item['quantity']
                })
        
        # Satışı kaydet
        if not errors:
            self.db.record_sale(total, payment_method, items_for_record)
            
            payment_text = "💵 Nakit" if payment_method == "cash" else "💳 Kredi Kartı"
            self._show_message(f"✅ Satış tamamlandı!\n{payment_text}: {total:,.2f} ₺", "green")
        else:
            self._show_message("⚠️ Bazı hatalar: " + ", ".join(errors), "orange")
        
        # Sepeti ve ödeme seçimini temizle
        self.cart.clear()
        self._refresh_cart()
        self.cash_selected.set(False)
        self.card_selected.set(False)
        self.payment_method.set("")
        
        # Footer'ı güncelle
        if self.on_update:
            self.on_update()
    
    def _clear_cart(self):
        """Sepeti temizle."""
        self.cart.clear()
        self._refresh_cart()
        self._show_message("🗑️ Sepet temizlendi", "gray")
    
    def _show_message(self, text: str, color: str):
        self.message_label.configure(text=text, text_color=color)
        self.after(3000, lambda: self.message_label.configure(text=""))
