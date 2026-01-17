"""
Gün Sonu Frame - Günlük satış raporu
Tarih seçerek geçmiş günlerin raporlarını görüntüleme
"""

import customtkinter as ctk
from typing import Callable
from datetime import datetime, date, timedelta


class GunSonuFrame(ctk.CTkFrame):
    def __init__(self, parent, database, on_update: Callable = None):
        super().__init__(parent, fg_color="transparent")
        
        self.db = database
        self.on_update = on_update
        self.selected_date = date.today()
        
        self._create_widgets()
        self._load_report()
    
    def _create_widgets(self):
        # Başlık
        header = ctk.CTkFrame(self, fg_color=("gray85", "gray20"), height=70)
        header.pack(fill="x", padx=20, pady=(20, 10))
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text="📊 GÜN SONU RAPORU",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left", padx=20, pady=15)
        
        # Tarih seçici
        date_frame = ctk.CTkFrame(header, fg_color="transparent")
        date_frame.pack(side="right", padx=20, pady=10)
        
        ctk.CTkButton(
            date_frame,
            text="◀",
            width=35,
            height=35,
            command=self._prev_day
        ).pack(side="left", padx=2)
        
        self.date_label = ctk.CTkLabel(
            date_frame,
            text=self.selected_date.strftime("%d.%m.%Y"),
            font=ctk.CTkFont(size=16, weight="bold"),
            width=120
        )
        self.date_label.pack(side="left", padx=10)
        
        ctk.CTkButton(
            date_frame,
            text="▶",
            width=35,
            height=35,
            command=self._next_day
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            date_frame,
            text="Bugün",
            width=60,
            height=35,
            command=self._go_today
        ).pack(side="left", padx=10)
        
        # Ana içerik
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=10)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)
        
        # ===== SOL TARAF - ÖZET KARTLARI =====
        left_frame = ctk.CTkFrame(content, fg_color=("gray90", "gray17"))
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=5)
        
        ctk.CTkLabel(
            left_frame,
            text="📋 GÜNLÜK ÖZET",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)
        
        # Toplam Satış Kartı
        total_card = ctk.CTkFrame(left_frame, fg_color=("gray75", "gray25"))
        total_card.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            total_card,
            text="💰 TOPLAM SATIŞ",
            font=ctk.CTkFont(size=14)
        ).pack(pady=(15, 5))
        
        self.total_label = ctk.CTkLabel(
            total_card,
            text="0.00 ₺",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=("#1B5E20", "#4CAF50")
        )
        self.total_label.pack(pady=(5, 15))
        
        # Nakit Kartı
        cash_card = ctk.CTkFrame(left_frame, fg_color=("#E8F5E9", "#1B5E20"))
        cash_card.pack(fill="x", padx=20, pady=10)
        
        cash_header = ctk.CTkFrame(cash_card, fg_color="transparent")
        cash_header.pack(fill="x", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(
            cash_header,
            text="💵 NAKİT",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left")
        
        self.cash_count_label = ctk.CTkLabel(
            cash_header,
            text="0 işlem",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.cash_count_label.pack(side="right")
        
        self.cash_total_label = ctk.CTkLabel(
            cash_card,
            text="0.00 ₺",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.cash_total_label.pack(pady=(5, 15))
        
        # Kredi Kartı Kartı
        card_card = ctk.CTkFrame(left_frame, fg_color=("#E3F2FD", "#0D47A1"))
        card_card.pack(fill="x", padx=20, pady=10)
        
        card_header = ctk.CTkFrame(card_card, fg_color="transparent")
        card_header.pack(fill="x", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(
            card_header,
            text="💳 KREDİ KARTI",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left")
        
        self.card_count_label = ctk.CTkLabel(
            card_header,
            text="0 işlem",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.card_count_label.pack(side="right")
        
        self.card_total_label = ctk.CTkLabel(
            card_card,
            text="0.00 ₺",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.card_total_label.pack(pady=(5, 15))
        
        # İşlem sayısı
        count_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        count_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            count_frame,
            text="Toplam İşlem:",
            font=ctk.CTkFont(size=14)
        ).pack(side="left")
        
        self.sale_count_label = ctk.CTkLabel(
            count_frame,
            text="0",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.sale_count_label.pack(side="right")
        
        # ===== SAĞ TARAF - İŞLEM LİSTESİ =====
        right_frame = ctk.CTkFrame(content, fg_color=("gray90", "gray17"))
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=5)
        
        ctk.CTkLabel(
            right_frame,
            text="📝 SATIŞLAR",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)
        
        # Liste başlıkları
        list_header = ctk.CTkFrame(right_frame, fg_color=("gray80", "gray25"))
        list_header.pack(fill="x", padx=10)
        
        headers = [("Saat", 60), ("Tutar", 100), ("Ödeme", 80)]
        for text, width in headers:
            ctk.CTkLabel(
                list_header,
                text=text,
                font=ctk.CTkFont(size=12, weight="bold"),
                width=width
            ).pack(side="left", padx=10, pady=8)
        
        # Satış listesi
        self.sales_list = ctk.CTkScrollableFrame(
            right_frame,
            fg_color="transparent"
        )
        self.sales_list.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Boş mesaj
        self.empty_label = ctk.CTkLabel(
            self.sales_list,
            text="Bu tarihte satış yok",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.empty_label.pack(pady=50)
    
    def _prev_day(self):
        """Önceki güne git."""
        self.selected_date -= timedelta(days=1)
        self._update_date_display()
        self._load_report()
    
    def _next_day(self):
        """Sonraki güne git."""
        if self.selected_date < date.today():
            self.selected_date += timedelta(days=1)
            self._update_date_display()
            self._load_report()
    
    def _go_today(self):
        """Bugüne git."""
        self.selected_date = date.today()
        self._update_date_display()
        self._load_report()
    
    def _update_date_display(self):
        """Tarih gösterimini güncelle."""
        display = self.selected_date.strftime("%d.%m.%Y")
        if self.selected_date == date.today():
            display += " (Bugün)"
        self.date_label.configure(text=display)
    
    def _load_report(self):
        """Raporu yükle."""
        # Özet bilgileri al
        summary = self.db.get_daily_summary(self.selected_date)
        
        # Kartları güncelle
        self.total_label.configure(text=f"{summary['grand_total']:,.2f} ₺")
        self.cash_total_label.configure(text=f"{summary['cash_total']:,.2f} ₺")
        self.cash_count_label.configure(text=f"{summary['cash_count']} işlem")
        self.card_total_label.configure(text=f"{summary['card_total']:,.2f} ₺")
        self.card_count_label.configure(text=f"{summary['card_count']} işlem")
        self.sale_count_label.configure(text=str(summary['total_sales']))
        
        # Satış listesini yükle
        self._load_sales_list()
    
    def _load_sales_list(self):
        """Satış listesini yükle."""
        # Temizle
        for widget in self.sales_list.winfo_children():
            widget.destroy()
        
        sales = self.db.get_daily_sales(self.selected_date)
        
        if not sales:
            self.empty_label = ctk.CTkLabel(
                self.sales_list,
                text="Bu tarihte satış yok",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            self.empty_label.pack(pady=50)
            return
        
        for sale in sales:
            # id, sale_date, total_amount, payment_method, items_json, created_at
            sale_time = datetime.fromisoformat(sale[5]).strftime("%H:%M")
            total = sale[2]
            method = "💵 Nakit" if sale[3] == "cash" else "💳 Kart"
            
            row = ctk.CTkFrame(self.sales_list, fg_color=("gray85", "gray22"), height=35)
            row.pack(fill="x", pady=1)
            row.pack_propagate(False)
            
            ctk.CTkLabel(
                row,
                text=sale_time,
                font=ctk.CTkFont(size=12),
                width=60
            ).pack(side="left", padx=10, pady=6)
            
            ctk.CTkLabel(
                row,
                text=f"{total:,.2f} ₺",
                font=ctk.CTkFont(size=12, weight="bold"),
                width=100
            ).pack(side="left", padx=10)
            
            ctk.CTkLabel(
                row,
                text=method,
                font=ctk.CTkFont(size=11),
                width=80
            ).pack(side="left", padx=10)
    
    def refresh(self):
        """Sayfayı yenile."""
        self._load_report()
