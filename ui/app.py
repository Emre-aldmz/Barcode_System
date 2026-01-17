"""
Barkod Stok Takip Sistemi - Ana Uygulama Penceresi
"""

import customtkinter as ctk
import sys
import os

# Proje kök dizinini path'e ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database
from ui.frames.sales import SalesFrame
from ui.frames.add_stock import AddStockFrame
from ui.frames.remove_stock import RemoveStockFrame
from ui.frames.depo import DepoFrame
from ui.frames.gun_sonu import GunSonuFrame
from ui.frames.butun_depo import ButunDepoFrame


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Pencere ayarları
        self.title("🏪 Barkod Stok Takip Sistemi")
        self.geometry("1150x780")
        self.minsize(1050, 700)
        
        # Tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Veritabanı Yolu Ayarla (PyInstaller uyumlu)
        if getattr(sys, 'frozen', False):
            # Eğer .exe olarak çalışıyorsa, exe'nin olduğu klasörü al
            application_path = os.path.dirname(sys.executable)
        else:
            # Normal python ile çalışıyorsa
            application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        db_path = os.path.join(application_path, "stock.db")
        self.db = Database(db_path)
        
        # Frame'ler için referanslar
        self.frames = {}
        self.current_frame = None
        
        # Depo alt menü durumu
        self.depo_expanded = False
        
        self._create_layout()
        
        # Başlangıçta SATIŞ sayfasını göster (ana sayfa)
        self._show_frame("sales")
    
    def _create_layout(self):
        # Grid yapılandırması
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # ===== HEADER =====
        header = ctk.CTkFrame(self, height=55, fg_color=("gray85", "gray20"))
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_propagate(False)
        
        title = ctk.CTkLabel(
            header,
            text="🏪 BARKOD STOK TAKİP SİSTEMİ",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(side="left", padx=20, pady=12)
        
        # Tema değiştirici
        theme_switch = ctk.CTkSwitch(
            header,
            text="🌙",
            command=self._toggle_theme,
            font=ctk.CTkFont(size=12),
            width=40
        )
        theme_switch.pack(side="right", padx=20)
        theme_switch.select()
        
        # ===== SIDEBAR =====
        self.sidebar = ctk.CTkFrame(self, width=170, fg_color=("gray90", "gray17"))
        self.sidebar.grid(row=1, column=0, sticky="ns", padx=(10, 0), pady=10)
        self.sidebar.grid_propagate(False)
        
        # SATIŞ butonu (Ana sayfa)
        self.sales_btn = ctk.CTkButton(
            self.sidebar,
            text="🛒 SATIŞ",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=50,
            fg_color="#6A1B9A",
            hover_color="#8E24AA",
            command=lambda: self._show_frame("sales")
        )
        self.sales_btn.pack(fill="x", padx=10, pady=(10, 5))
        
        # DEPO butonu (Expandable)
        self.depo_btn = ctk.CTkButton(
            self.sidebar,
            text="📦 DEPO ▼",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=50,
            fg_color="#1565C0",
            hover_color="#1976D2",
            command=self._toggle_depo_menu
        )
        self.depo_btn.pack(fill="x", padx=10, pady=5)
        
        # Depo alt menü container
        self.depo_submenu = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        
        # Alt menü butonları (başlangıçta gizli)
        self.add_btn = ctk.CTkButton(
            self.depo_submenu,
            text="   ➕ Stok Ekle",
            font=ctk.CTkFont(size=13),
            height=40,
            fg_color=("#2E7D32", "#1B5E20"),
            hover_color="#388E3C",
            anchor="w",
            command=lambda: self._show_frame("add")
        )
        self.add_btn.pack(fill="x", padx=20, pady=2)
        
        self.remove_btn = ctk.CTkButton(
            self.depo_submenu,
            text="   ➖ Stok Çıkar",
            font=ctk.CTkFont(size=13),
            height=40,
            fg_color=("#C62828", "#B71C1C"),
            hover_color="#D32F2F",
            anchor="w",
            command=lambda: self._show_frame("remove")
        )
        self.remove_btn.pack(fill="x", padx=20, pady=2)
        
        self.list_btn = ctk.CTkButton(
            self.depo_submenu,
            text="   📋 Liste/Düzenle",
            font=ctk.CTkFont(size=13),
            height=40,
            fg_color=("#455A64", "#37474F"),
            hover_color="#546E7A",
            anchor="w",
            command=lambda: self._show_frame("depo")
        )
        self.list_btn.pack(fill="x", padx=20, pady=2)
        
        self.butun_depo_btn = ctk.CTkButton(
            self.depo_submenu,
            text="   📦 Bütün Depo",
            font=ctk.CTkFont(size=13),
            height=40,
            fg_color=("#5D4037", "#4E342E"),
            hover_color="#6D4C41",
            anchor="w",
            command=lambda: self._show_frame("butun_depo")
        )
        self.butun_depo_btn.pack(fill="x", padx=20, pady=2)
        
        # GÜN SONU butonu
        self.gunsonu_btn = ctk.CTkButton(
            self.sidebar,
            text="📊 GÜN SONU",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=50,
            fg_color="#E65100",
            hover_color="#F57C00",
            command=lambda: self._show_frame("gunsonu")
        )
        self.gunsonu_btn.pack(fill="x", padx=10, pady=5)
        
        # ===== MAIN CONTENT =====
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self.main_content.grid_rowconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)
        
        # Frame'leri oluştur
        self.frames["sales"] = SalesFrame(self.main_content, self.db, self._on_sale_complete)
        self.frames["add"] = AddStockFrame(self.main_content, self.db, self._on_stock_change)
        self.frames["remove"] = RemoveStockFrame(self.main_content, self.db, self._on_stock_change)
        self.frames["depo"] = DepoFrame(self.main_content, self.db, self._on_stock_change)
        self.frames["butun_depo"] = ButunDepoFrame(self.main_content, self.db, self._on_stock_change)
        self.frames["gunsonu"] = GunSonuFrame(self.main_content, self.db, None)
        
        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")
    
    def _toggle_depo_menu(self):
        """Depo alt menüsünü aç/kapa."""
        if self.depo_expanded:
            self.depo_submenu.pack_forget()
            self.depo_btn.configure(text="📦 DEPO ▼")
            self.depo_expanded = False
        else:
            # Depo butonunun hemen altına ekle
            self.depo_submenu.pack(fill="x", after=self.depo_btn)
            self.depo_btn.configure(text="📦 DEPO ▲")
            self.depo_expanded = True
    
    def _show_frame(self, frame_name: str):
        """Belirtilen frame'i göster."""
        if frame_name in self.frames:
            # DEPO alt sayfaları - aralarında geçişte veya dışarı çıkınca resetle
            depo_frames = ["add", "remove", "depo", "butun_depo"]
            
            # Önceki frame DEPO altındaysa ve farklı bir sayfaya gidiyorsak resetle
            if self.current_frame in depo_frames and self.current_frame != frame_name:
                if hasattr(self.frames[self.current_frame], 'reset'):
                    self.frames[self.current_frame].reset()
            
            # Hedef sayfaya refresh
            if frame_name == "depo":
                self.frames["depo"].refresh()
            elif frame_name == "gunsonu":
                self.frames["gunsonu"].refresh()
            elif frame_name == "butun_depo":
                self.frames["butun_depo"].refresh()
            
            self.frames[frame_name].tkraise()
            self.current_frame = frame_name
            
            # Buton vurgulamalarını güncelle
            self._update_button_highlights(frame_name)
            
            # Sayfaya göre doğru alana focus ver
            self.after(100, lambda: self._focus_frame_input(frame_name))
    
    def _focus_frame_input(self, frame_name: str):
        """Sayfa değiştiğinde uygun input alanına focus ver."""
        frame = self.frames.get(frame_name)
        if not frame:
            return
        
        # Her sayfanın ana giriş alanına focus
        if frame_name == "sales" and hasattr(frame, 'barcode_entry'):
            frame.barcode_entry.focus_set()
        elif frame_name == "add" and hasattr(frame, 'product_id_entry'):
            frame.product_id_entry.focus_set()
        elif frame_name == "remove" and hasattr(frame, 'search_entry'):
            frame.search_entry.focus_set()
        elif frame_name == "depo" and hasattr(frame, 'search_entry'):
            frame.search_entry.focus_set()
    
    def _update_button_highlights(self, active_frame: str):
        """Aktif butonun vurgusunu güncelle."""
        # Ana butonlar
        self.sales_btn.configure(
            fg_color=("gray60", "gray40") if active_frame == "sales" else "#6A1B9A"
        )
        self.gunsonu_btn.configure(
            fg_color=("gray60", "gray40") if active_frame == "gunsonu" else "#E65100"
        )
        
        # Depo alt menü
        depo_active = active_frame in ["add", "remove", "depo", "butun_depo"]
        self.depo_btn.configure(
            fg_color=("gray60", "gray40") if depo_active else "#1565C0"
        )
    
    def _on_sale_complete(self):
        """Satış tamamlandığında."""
        # Gün sonu raporunu güncelle
        if "gunsonu" in self.frames:
            self.frames["gunsonu"].refresh()
    
    def _on_stock_change(self):
        """Stok değiştiğinde."""
        # Depo sayfasını güncelle
        if "depo" in self.frames:
            self.frames["depo"].refresh()
    
    def _toggle_theme(self):
        """Tema değiştir."""
        current = ctk.get_appearance_mode()
        if current == "Dark":
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("dark")
    
    def on_closing(self):
        """Uygulama kapatılırken."""
        self.db.close()
        self.destroy()


def run():
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    run()
