"""
Depo Frame - Stok Listesi / Düzenle
Sadece arama yapınca ürünler görünür (performans için)
Fiyat düzenleme özelliği ile
"""

import customtkinter as ctk
from typing import Callable


class DepoFrame(ctk.CTkFrame):
    def __init__(self, parent, database, on_update: Callable = None):
        super().__init__(parent, fg_color="transparent")
        
        self.db = database
        self.on_update = on_update
        
        self._create_widgets()
    
    def _create_widgets(self):
        # Başlık
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            header, 
            text="📦 STOK LİSTESİ / DÜZENLE",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left")
        
        # Arama alanı
        search_frame = ctk.CTkFrame(header, fg_color="transparent")
        search_frame.pack(side="right")
        
        self.search_type = ctk.CTkSegmentedButton(
            search_frame,
            values=["Tümü", "Ürün ID", "Barkod", "İsim"],
            command=self._on_search_type_change
        )
        self.search_type.set("Tümü")
        self.search_type.pack(side="left", padx=10)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Ürün ara...",
            width=250,
            height=38
        )
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<Return>", lambda e: self._search_products())
        
        search_btn = ctk.CTkButton(
            search_frame,
            text="Ara",
            width=60,
            height=38,
            command=self._search_products
        )
        search_btn.pack(side="left", padx=5)
        
        # Tablo başlıkları
        headers_frame = ctk.CTkFrame(self, fg_color=("gray80", "gray25"))
        headers_frame.pack(fill="x", padx=20, pady=(10, 0))
        
        headers = [
            ("Ürün ID", 100),
            ("Barkod", 110),
            ("Ürün Adı", 160),
            ("Beden", 55),
            ("Adet", 55),
            ("Fiyat", 75),
            ("Toplam", 85),
            ("İşlem", 80)
        ]
        
        for text, width in headers:
            ctk.CTkLabel(
                headers_frame,
                text=text,
                font=ctk.CTkFont(size=12, weight="bold"),
                width=width
            ).pack(side="left", padx=2, pady=10)
        
        # Scrollable liste
        self.list_container = ctk.CTkScrollableFrame(
            self,
            fg_color=("gray95", "gray17"),
            height=300
        )
        self.list_container.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Başlangıç mesajı
        self.placeholder = ctk.CTkLabel(
            self.list_container,
            text="🔍 Ürün aramak için yukarıdaki arama kutusunu kullanın\n\nÖrnek: Ürün ID, barkod veya ürün adı ile arayın",
            font=ctk.CTkFont(size=16),
            text_color="gray",
            justify="center"
        )
        self.placeholder.pack(pady=80)
        
        # ===== FOOTER - TOPLAM BİLGİLER =====
        self.footer = ctk.CTkFrame(self, fg_color=("gray85", "gray22"), height=50)
        self.footer.pack(fill="x", padx=20, pady=(0, 10))
        self.footer.pack_propagate(False)
        
        self.total_value_label = ctk.CTkLabel(
            self.footer,
            text="💰 TOPLAM STOK DEĞERİ: 0.00 ₺",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.total_value_label.pack(side="left", padx=20, pady=12)
        
        self.total_qty_label = ctk.CTkLabel(
            self.footer,
            text="📦 Toplam: 0 adet",
            font=ctk.CTkFont(size=14)
        )
        self.total_qty_label.pack(side="right", padx=20, pady=12)
        
        self.result_count_label = ctk.CTkLabel(
            self.footer,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.result_count_label.pack(side="right", padx=20, pady=12)
        
        # Mesaj alanı
        self.message_label = ctk.CTkLabel(
            self, 
            text="",
            font=ctk.CTkFont(size=14)
        )
        self.message_label.pack(pady=5)
        
        # Totalleri güncelle
        self._update_totals()
    
    def _on_search_type_change(self, value):
        """Arama tipi değiştiğinde."""
        placeholders = {
            "Tümü": "🔍 Tümünde ara...",
            "Ürün ID": "🔍 Ürün ID ara...",
            "Barkod": "🔍 Barkod ara...",
            "İsim": "🔍 Ürün adı ara..."
        }
        self.search_entry.configure(placeholder_text=placeholders.get(value, "🔍 Ara..."))
    
    def _search_products(self):
        """Ürünleri ara ve listele."""
        search_term = self.search_entry.get().strip()
        
        if not search_term:
            self._show_message("❌ Arama terimi girin!", "red")
            return
        
        # Arama tipini belirle
        search_type_map = {
            "Tümü": "all",
            "Ürün ID": "product_id",
            "Barkod": "barcode",
            "İsim": "name"
        }
        search_type = search_type_map.get(self.search_type.get(), "all")
        
        # Ara
        products = self.db.search_products(search_term, search_type)
        
        # Sonuçları göster
        self._load_products(products)
    
    def _load_products(self, products):
        """Ürünleri listele."""
        # Temizle
        for widget in self.list_container.winfo_children():
            widget.destroy()
        
        if not products:
            self.placeholder = ctk.CTkLabel(
                self.list_container,
                text="❌ Ürün bulunamadı",
                font=ctk.CTkFont(size=16),
                text_color="gray"
            )
            self.placeholder.pack(pady=80)
            self.result_count_label.configure(text="")
            return
        
        self.result_count_label.configure(text=f"Bulunan: {len(products)} kayıt")
        
        for product in products:
            self._add_product_row(product)
    
    def _add_product_row(self, product):
        """Tek bir ürün satırı ekle."""
        row_id = product[0]
        product_id = product[1]
        barcode = product[2]
        name = product[3]
        size = product[4] or "-"
        quantity = product[5]
        price = product[6]
        total = quantity * price
        
        row = ctk.CTkFrame(self.list_container, fg_color=("gray90", "gray20"), height=40)
        row.pack(fill="x", pady=1)
        row.pack_propagate(False)
        
        data = [
            (product_id, 100),
            (barcode, 110),
            (name[:18] + "..." if len(name) > 18 else name, 160),
            (size, 55),
            (str(quantity), 55),
            (f"{price:.2f} ₺", 75),
            (f"{total:.2f} ₺", 85)
        ]
        
        for text, width in data:
            ctk.CTkLabel(
                row,
                text=text,
                font=ctk.CTkFont(size=11),
                width=width,
                anchor="w"
            ).pack(side="left", padx=2, pady=6)
        
        # Ayarlar butonu (menü açar)
        settings_btn = ctk.CTkButton(
            row,
            text="⚙️",
            width=32,
            height=28,
            fg_color=("#1976D2", "#0D47A1"),
            hover_color=("#2196F3", "#1976D2"),
            command=lambda pid=product_id, bc=barcode, p=price, s=size, rid=row_id: self._show_edit_menu(pid, bc, p, s, rid)
        )
        settings_btn.pack(side="left", padx=2)
        
        # Silme butonu
        ctk.CTkButton(
            row,
            text="🗑️",
            width=32,
            height=28,
            fg_color=("#E53935", "#C62828"),
            hover_color=("#F44336", "#E53935"),
            command=lambda rid=row_id: self._delete_product(rid)
        ).pack(side="left", padx=2)
    
    def _show_edit_menu(self, product_id: str, barcode: str, price: float, size: str, row_id: int):
        """Düzenleme menüsü göster."""
        # Popup pencere oluştur
        menu_window = ctk.CTkToplevel(self)
        menu_window.title("⚙️ Düzenle")
        menu_window.geometry("280x200")
        menu_window.resizable(False, False)
        
        # Ortala
        menu_window.update()
        x = self.winfo_rootx() + 200
        y = self.winfo_rooty() + 100
        menu_window.geometry(f"+{x}+{y}")
        
        # Pencere görünür olduktan sonra grab
        menu_window.after(100, lambda: menu_window.grab_set())
        
        # Başlık
        ctk.CTkLabel(
            menu_window,
            text=f"📦 {product_id} - {size}",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(15, 5))
        
        ctk.CTkLabel(
            menu_window,
            text=f"Barkod: {barcode}",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).pack(pady=(0, 15))
        
        # Fiyat Düzenle Butonu
        ctk.CTkButton(
            menu_window,
            text="💰 Fiyat Düzenle (Tüm Bedenler)",
            font=ctk.CTkFont(size=13),
            height=40,
            fg_color=("#2E7D32", "#1B5E20"),
            hover_color=("#388E3C", "#2E7D32"),
            command=lambda: [menu_window.destroy(), self._edit_price(product_id, price)]
        ).pack(fill="x", padx=20, pady=5)
        
        # Beden Düzenle Butonu
        ctk.CTkButton(
            menu_window,
            text="📏 Beden Düzenle (Sadece Bu Ürün)",
            font=ctk.CTkFont(size=13),
            height=40,
            fg_color=("#1565C0", "#0D47A1"),
            hover_color=("#1976D2", "#1565C0"),
            command=lambda: [menu_window.destroy(), self._edit_size(row_id, barcode, size)]
        ).pack(fill="x", padx=20, pady=5)
        
        # İptal Butonu
        ctk.CTkButton(
            menu_window,
            text="İptal",
            font=ctk.CTkFont(size=12),
            height=30,
            fg_color=("gray60", "gray40"),
            hover_color=("gray50", "gray30"),
            command=menu_window.destroy
        ).pack(fill="x", padx=20, pady=(10, 15))
    
    def _edit_price(self, product_id: str, current_price: float):
        """Fiyat düzenleme dialogu."""
        dialog = ctk.CTkInputDialog(
            text=f"Ürün ID: {product_id}\nMevcut fiyat: {current_price:.2f} ₺\n\nYeni fiyat girin:",
            title="💰 Fiyat Güncelle"
        )
        result = dialog.get_input()
        
        if result:
            try:
                new_price = float(result.replace(",", ".").replace("₺", "").strip())
                if new_price < 0:
                    raise ValueError()
                
                success, message = self.db.update_price_by_product_id(product_id, new_price)
                
                if success:
                    self._show_message(f"✅ {message}", "green")
                    self._search_products()  # Listeyi yenile
                    self._update_totals()
                    if self.on_update:
                        self.on_update()
                else:
                    self._show_message(f"❌ {message}", "red")
            except ValueError:
                self._show_message("❌ Geçersiz fiyat!", "red")
    
    def _edit_size(self, row_id: int, barcode: str, current_size: str):
        """Beden düzenleme dialogu - sadece bu barkod için."""
        # Popup pencere
        size_window = ctk.CTkToplevel(self)
        size_window.title("📏 Beden Düzenle")
        size_window.geometry("320x300")
        size_window.resizable(False, False)
        
        # Ortala
        size_window.update()
        x = self.winfo_rootx() + 200
        y = self.winfo_rooty() + 100
        size_window.geometry(f"+{x}+{y}")
        
        # Pencere görünür olduktan sonra grab
        size_window.after(100, lambda: size_window.grab_set())
        
        ctk.CTkLabel(
            size_window,
            text=f"Barkod: {barcode}",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(pady=(15, 5))
        
        ctk.CTkLabel(
            size_window,
            text=f"Mevcut Beden: {current_size}",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(5, 15))
        
        ctk.CTkLabel(
            size_window,
            text="Yeni beden seçin:",
            font=ctk.CTkFont(size=12)
        ).pack(pady=(0, 10))
        
        # Beden seçici - güncellenmiş bedenler
        selected_size = ctk.StringVar(value=current_size)
        sizes = ["XS", "S", "M", "L", "XL", "XXL", "STD"]
        
        size_frame = ctk.CTkFrame(size_window, fg_color="transparent")
        size_frame.pack(pady=10)
        
        for i, size in enumerate(sizes):
            btn = ctk.CTkRadioButton(
                size_frame,
                text=size,
                variable=selected_size,
                value=size,
                font=ctk.CTkFont(size=12)
            )
            btn.grid(row=i//4, column=i%4, padx=8, pady=5)
        
        def save_size():
            new_size = selected_size.get()
            success, message = self.db.update_product(row_id, size=new_size)
            
            if success:
                size_window.destroy()
                self._show_message(f"✅ Beden güncellendi: {new_size or '-'}", "green")
                self._search_products()
            else:
                self._show_message(f"❌ {message}", "red")
        
        ctk.CTkButton(
            size_window,
            text="💾 Kaydet",
            font=ctk.CTkFont(size=13),
            height=35,
            fg_color=("#2E7D32", "#1B5E20"),
            hover_color=("#388E3C", "#2E7D32"),
            command=save_size
        ).pack(fill="x", padx=30, pady=(15, 10))
    
    def _delete_product(self, row_id: int):
        """Ürünü sil."""
        dialog = ctk.CTkInputDialog(
            text="Silmek için 'EVET' yazın:",
            title="Ürün Silme Onayı"
        )
        result = dialog.get_input()
        
        if result and result.upper() == "EVET":
            success, message = self.db.delete_product(row_id)
            
            if success:
                self._show_message(f"✅ {message}", "green")
                self._search_products()  # Listeyi yenile
                self._update_totals()
                if self.on_update:
                    self.on_update()
            else:
                self._show_message(f"❌ {message}", "red")
    
    def _update_totals(self):
        """Toplam değerleri güncelle."""
        total_value = self.db.get_total_value()
        total_qty = self.db.get_total_quantity()
        
        self.total_value_label.configure(text=f"💰 TOPLAM STOK DEĞERİ: {total_value:,.2f} ₺")
        self.total_qty_label.configure(text=f"📦 Toplam: {total_qty} adet")
    
    def refresh(self):
        """Sayfayı yenile."""
        self._update_totals()
    
    def reset(self):
        """Sayfa değiştiğinde çağrılır - arama sıfırla."""
        self.search_entry.delete(0, "end")
        for widget in self.list_container.winfo_children():
            widget.destroy()
        self.placeholder = ctk.CTkLabel(
            self.list_container,
            text="🔍 Ürün aramak için yukarıdaki arama kutusunu kullanın",
            font=ctk.CTkFont(size=16),
            text_color="gray",
            justify="center"
        )
        self.placeholder.pack(pady=80)
        self.result_count_label.configure(text="")
        self.message_label.configure(text="")
        self._update_totals()
    
    def _show_message(self, text: str, color: str):
        self.message_label.configure(text=text, text_color=color)
        self.after(3000, lambda: self.message_label.configure(text=""))

