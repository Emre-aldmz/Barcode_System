"""
Stok Ekleme Frame
"""

import customtkinter as ctk
from typing import Callable, Dict


class AddStockFrame(ctk.CTkFrame):
    def __init__(self, parent, database, on_update: Callable = None):
        super().__init__(parent, fg_color="transparent")
        
        self.db = database
        self.on_update = on_update
        
        # Beden seçimi için değişkenler
        self.size_vars: Dict[str, ctk.BooleanVar] = {}
        self.selected_size = ""
        
        self._create_widgets()
    
    def _create_widgets(self):
        # Başlık frame
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header, 
            text="➕ YENİ ÜRÜN EKLE",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(side="left")
        
        # Yenile butonu
        refresh_btn = ctk.CTkButton(
            header,
            text="🔄 Yeni Ürün",
            width=100,
            height=35,
            font=ctk.CTkFont(size=12),
            fg_color=("#FF6F00", "#E65100"),
            hover_color=("#FF8F00", "#FF6F00"),
            command=self._reset_all
        )
        refresh_btn.pack(side="right")
        
        # Form container
        form = ctk.CTkFrame(self, fg_color=("gray90", "gray17"))
        form.pack(fill="x", padx=40, pady=10)
        
        # Ürün ID (Model Kodu)
        product_id_label = ctk.CTkLabel(form, text="Ürün ID:", font=ctk.CTkFont(size=14))
        product_id_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        self.product_id_entry = ctk.CTkEntry(
            form, 
            placeholder_text="Model kodu (örn: TSH001)...",
            width=300,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.product_id_entry.grid(row=0, column=1, padx=20, pady=(20, 10), sticky="w")
        self.product_id_entry.bind("<Return>", lambda e: self.barcode_entry.focus())
        
        # Bilgi etiketi
        info_label = ctk.CTkLabel(
            form, 
            text="💡 Aynı modelin tüm bedenlerini gruplar",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        info_label.grid(row=0, column=2, padx=10, pady=(20, 10), sticky="w")
        
        # Barkod
        barcode_label = ctk.CTkLabel(form, text="Barkod:", font=ctk.CTkFont(size=14))
        barcode_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        self.barcode_entry = ctk.CTkEntry(
            form, 
            placeholder_text="Barkodu girin veya okutun...",
            width=300,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.barcode_entry.grid(row=1, column=1, padx=20, pady=10, sticky="w")
        self.barcode_entry.bind("<Return>", lambda e: self.name_entry.focus())
        
        # Ürün Adı
        name_label = ctk.CTkLabel(form, text="Ürün Adı:", font=ctk.CTkFont(size=14))
        name_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        
        self.name_entry = ctk.CTkEntry(
            form, 
            placeholder_text="Ürün adını girin...",
            width=300,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.name_entry.grid(row=2, column=1, padx=20, pady=10, sticky="w")
        
        # Beden (Checkbox - kare kutular)
        size_label = ctk.CTkLabel(form, text="Beden:", font=ctk.CTkFont(size=14))
        size_label.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        
        size_frame = ctk.CTkFrame(form, fg_color="transparent")
        size_frame.grid(row=3, column=1, padx=20, pady=10, sticky="w")
        
        sizes = ["XS", "S", "M", "L", "XL", "XXL", "STD"]
        for size in sizes:
            var = ctk.BooleanVar(value=False)
            self.size_vars[size] = var
            
            cb = ctk.CTkCheckBox(
                size_frame, 
                text=size, 
                variable=var,
                font=ctk.CTkFont(size=13),
                checkbox_width=22,
                checkbox_height=22,
                corner_radius=4,
                command=lambda s=size: self._on_size_selected(s)
            )
            cb.pack(side="left", padx=5)
        
        # Adet (boş başlar)
        quantity_label = ctk.CTkLabel(form, text="Adet:", font=ctk.CTkFont(size=14))
        quantity_label.grid(row=4, column=0, padx=20, pady=10, sticky="w")
        
        self.quantity_entry = ctk.CTkEntry(
            form, 
            placeholder_text="Adet girin...",
            width=150,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.quantity_entry.grid(row=4, column=1, padx=20, pady=10, sticky="w")
        # Adet boş başlar - default yok
        
        # Fiyat
        price_label = ctk.CTkLabel(form, text="Fiyat (₺):", font=ctk.CTkFont(size=14))
        price_label.grid(row=5, column=0, padx=20, pady=10, sticky="w")
        
        self.price_entry = ctk.CTkEntry(
            form, 
            placeholder_text="0.00",
            width=150,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.price_entry.grid(row=5, column=1, padx=20, pady=(10, 20), sticky="w")
        
        # Kaydet butonu
        save_btn = ctk.CTkButton(
            self,
            text="💾  KAYDET",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=200,
            height=50,
            command=self._save_product,
            fg_color=("#2E7D32", "#1B5E20"),
            hover_color=("#388E3C", "#2E7D32")
        )
        save_btn.pack(pady=30)
        
        # Mesaj alanı
        self.message_label = ctk.CTkLabel(
            self, 
            text="",
            font=ctk.CTkFont(size=14)
        )
        self.message_label.pack(pady=10)
    
    def _on_size_selected(self, selected: str):
        """Beden seçildiğinde diğerlerini kaldır (tek seçim)."""
        for size, var in self.size_vars.items():
            if size != selected:
                var.set(False)
        
        if self.size_vars[selected].get():
            self.selected_size = selected
        else:
            self.selected_size = ""
    
    def _get_selected_size(self) -> str:
        """Seçili bedeni döndür."""
        for size, var in self.size_vars.items():
            if var.get():
                return size
        return ""
    
    def _save_product(self):
        product_id = self.product_id_entry.get().strip()
        barcode = self.barcode_entry.get().strip()
        name = self.name_entry.get().strip()
        size = self._get_selected_size()
        
        # Validasyon
        if not product_id:
            self._show_message("❌ Ürün ID gerekli!", "red")
            return
        
        if not barcode:
            self._show_message("❌ Barkod gerekli!", "red")
            return
        
        if not name:
            self._show_message("❌ Ürün adı gerekli!", "red")
            return
        
        if not size:
            self._show_message("❌ Beden seçin!", "red")
            return
        
        quantity_str = self.quantity_entry.get().strip()
        if not quantity_str:
            self._show_message("❌ Adet girin!", "red")
            return
        
        try:
            quantity = int(quantity_str)
            if quantity <= 0:
                raise ValueError()
        except ValueError:
            self._show_message("❌ Geçersiz adet!", "red")
            return
        
        try:
            price = float(self.price_entry.get() or "0")
            if price < 0:
                raise ValueError()
        except ValueError:
            self._show_message("❌ Geçersiz fiyat!", "red")
            return
        
        # Kaydet
        success, message = self.db.add_product(product_id, barcode, name, size, quantity, price)
        
        if success:
            self._show_message(f"✅ {message}", "green")
            self._clear_form()
            if self.on_update:
                self.on_update()
        else:
            self._show_message(f"❌ {message}", "red")
    
    def _show_message(self, text: str, color: str):
        self.message_label.configure(text=text, text_color=color)
        self.after(3000, lambda: self.message_label.configure(text=""))
    
    def _clear_form(self):
        """Ürün ekledikten sonra: barkod, adet, beden sıfırla - ID, isim, fiyat kalır."""
        self.barcode_entry.delete(0, "end")
        self.quantity_entry.delete(0, "end")
        # Bedeni sıfırla
        for var in self.size_vars.values():
            var.set(False)
        self.selected_size = ""
        self.barcode_entry.focus()
    
    def _reset_all(self):
        """Tüm formu sıfırla - yeni ürün için hazırla."""
        self.product_id_entry.delete(0, "end")
        self.barcode_entry.delete(0, "end")
        self.name_entry.delete(0, "end")
        for var in self.size_vars.values():
            var.set(False)
        self.selected_size = ""
        self.quantity_entry.delete(0, "end")
        self.price_entry.delete(0, "end")
        self.product_id_entry.focus()
        self._show_message("🔄 Form sıfırlandı", "gray")
    
    def reset(self):
        """Sayfa değiştiğinde çağrılır - formu sıfırla."""
        self._reset_all()
        self.message_label.configure(text="")
