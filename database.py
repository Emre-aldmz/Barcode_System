"""
Barkod Stok Takip Sistemi - Veritabanı Modülü
SQLite ile stok yönetimi ve satış kayıtları
"""

import sqlite3
from datetime import datetime, date
from typing import List, Tuple, Optional, Dict
import os


class Database:
    def __init__(self, db_path: str = "stock.db"):
        """Veritabanı bağlantısını başlat ve tabloları oluştur."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()
        self._migrate_tables()
    
    def _create_tables(self):
        """Gerekli tabloları oluştur."""
        # Ürünler tablosu
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT NOT NULL,
                barcode TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                size TEXT DEFAULT '',
                quantity INTEGER DEFAULT 0,
                price REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Satışlar tablosu (gün sonu için)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_date DATE NOT NULL,
                total_amount REAL NOT NULL,
                payment_method TEXT NOT NULL,
                items_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        
        # Performans için index'ler
        self._create_indexes()
    
    def _create_indexes(self):
        """Büyük veri setleri için index'ler oluştur."""
        indexes = [
            # Ürünler tablosu
            "CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(barcode)",
            "CREATE INDEX IF NOT EXISTS idx_products_product_id ON products(product_id)",
            "CREATE INDEX IF NOT EXISTS idx_products_name ON products(name)",
            # Satışlar tablosu
            "CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date)",
            "CREATE INDEX IF NOT EXISTS idx_sales_method ON sales(payment_method)",
        ]
        
        for idx in indexes:
            try:
                self.cursor.execute(idx)
            except sqlite3.OperationalError:
                pass  # Index zaten var
        
        self.conn.commit()
    
    def _migrate_tables(self):
        """Mevcut tabloya product_id kolonu ekle (migration)."""
        try:
            self.cursor.execute("SELECT product_id FROM products LIMIT 1")
        except sqlite3.OperationalError:
            self.cursor.execute("ALTER TABLE products ADD COLUMN product_id TEXT DEFAULT ''")
            self.conn.commit()
    
    # ========== ÜRÜN İŞLEMLERİ ==========
    
    def add_product(self, product_id: str, barcode: str, name: str, size: str = "", 
                    quantity: int = 0, price: float = 0.0) -> Tuple[bool, str]:
        """Yeni ürün ekle veya mevcut ürünün stokunu artır."""
        try:
            existing = self.search_by_barcode(barcode)
            
            if existing:
                new_quantity = existing[5] + quantity
                self.cursor.execute('''
                    UPDATE products 
                    SET quantity = ?, updated_at = ?
                    WHERE barcode = ?
                ''', (new_quantity, datetime.now(), barcode))
                self.conn.commit()
                return True, f"Stok güncellendi! Yeni miktar: {new_quantity}"
            else:
                self.cursor.execute('''
                    INSERT INTO products (product_id, barcode, name, size, quantity, price)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (product_id, barcode, name, size, quantity, price))
                self.conn.commit()
                return True, "Yeni ürün başarıyla eklendi!"
                
        except sqlite3.IntegrityError:
            return False, "Bu barkod zaten mevcut!"
        except Exception as e:
            return False, f"Hata: {str(e)}"
    
    def remove_stock(self, barcode: str, quantity: int) -> Tuple[bool, str]:
        """Ürün stokunu azalt."""
        try:
            product = self.search_by_barcode(barcode)
            
            if not product:
                return False, "Ürün bulunamadı!"
            
            current_quantity = product[5]
            
            if quantity > current_quantity:
                return False, f"Yetersiz stok! Mevcut: {current_quantity}"
            
            new_quantity = current_quantity - quantity
            
            self.cursor.execute('''
                UPDATE products 
                SET quantity = ?, updated_at = ?
                WHERE barcode = ?
            ''', (new_quantity, datetime.now(), barcode))
            self.conn.commit()
            
            return True, f"Stok güncellendi! Kalan: {new_quantity}"
            
        except Exception as e:
            return False, f"Hata: {str(e)}"
    
    def update_product(self, row_id: int, product_id: str = None, barcode: str = None, 
                       name: str = None, size: str = None,
                       quantity: int = None, price: float = None) -> Tuple[bool, str]:
        """Ürün bilgilerini güncelle."""
        try:
            updates = []
            values = []
            
            if product_id is not None:
                updates.append("product_id = ?")
                values.append(product_id)
            if barcode is not None:
                updates.append("barcode = ?")
                values.append(barcode)
            if name is not None:
                updates.append("name = ?")
                values.append(name)
            if size is not None:
                updates.append("size = ?")
                values.append(size)
            if quantity is not None:
                updates.append("quantity = ?")
                values.append(quantity)
            if price is not None:
                updates.append("price = ?")
                values.append(price)
            
            if not updates:
                return False, "Güncellenecek alan yok!"
            
            updates.append("updated_at = ?")
            values.append(datetime.now())
            values.append(row_id)
            
            query = f"UPDATE products SET {', '.join(updates)} WHERE id = ?"
            self.cursor.execute(query, values)
            self.conn.commit()
            
            return True, "Ürün güncellendi!"
            
        except sqlite3.IntegrityError:
            return False, "Bu barkod başka bir üründe kullanılıyor!"
        except Exception as e:
            return False, f"Hata: {str(e)}"
    
    def update_price_by_product_id(self, product_id: str, new_price: float) -> Tuple[bool, str]:
        """
        Aynı ürün ID'sine sahip TÜM bedenlerin fiyatını güncelle.
        
        Args:
            product_id: Ürün/Model kodu
            new_price: Yeni fiyat
        
        Returns:
            (success, message) tuple
        """
        try:
            self.cursor.execute('''
                UPDATE products 
                SET price = ?, updated_at = ?
                WHERE product_id = ?
            ''', (new_price, datetime.now(), product_id))
            self.conn.commit()
            
            count = self.cursor.rowcount
            if count > 0:
                return True, f"{count} ürün güncellendi! Yeni fiyat: {new_price:.2f} ₺"
            else:
                return False, "Ürün bulunamadı!"
                
        except Exception as e:
            return False, f"Hata: {str(e)}"
    
    def delete_product(self, row_id: int) -> Tuple[bool, str]:
        """Ürünü sil."""
        try:
            self.cursor.execute("DELETE FROM products WHERE id = ?", (row_id,))
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                return True, "Ürün silindi!"
            else:
                return False, "Ürün bulunamadı!"
                
        except Exception as e:
            return False, f"Hata: {str(e)}"
    
    def get_all_products(self) -> List[Tuple]:
        """Tüm ürünleri getir."""
        self.cursor.execute('''
            SELECT id, product_id, barcode, name, size, quantity, price, created_at, updated_at
            FROM products
            ORDER BY product_id, size
        ''')
        return self.cursor.fetchall()
    
    def search_by_barcode(self, barcode: str) -> Optional[Tuple]:
        """Barkod ile ürün ara - tek ürün döner."""
        self.cursor.execute('''
            SELECT id, product_id, barcode, name, size, quantity, price, created_at, updated_at
            FROM products
            WHERE barcode = ?
        ''', (barcode,))
        return self.cursor.fetchone()
    
    def search_by_product_id(self, product_id: str) -> List[Tuple]:
        """Ürün ID ile ara - aynı modelin TÜM bedenlerini döner."""
        self.cursor.execute('''
            SELECT id, product_id, barcode, name, size, quantity, price, created_at, updated_at
            FROM products
            WHERE product_id = ?
            ORDER BY size
        ''', (product_id,))
        return self.cursor.fetchall()
    
    def search_products(self, search_term: str, search_type: str = "all") -> List[Tuple]:
        """Ürün ara - TAM EŞLEŞMEile (exact match)."""
        # Tam eşleşme için wildcard yok
        if search_type == "product_id":
            query = "WHERE product_id = ?"
        elif search_type == "barcode":
            query = "WHERE barcode = ?"
        elif search_type == "name":
            query = "WHERE name = ?"
        else:  # all - herhangi birinde tam eşleşme
            query = "WHERE product_id = ? OR barcode = ? OR name = ?"
        
        sql = f'''
            SELECT id, product_id, barcode, name, size, quantity, price, created_at, updated_at
            FROM products
            {query}
            ORDER BY product_id, size
            LIMIT 100
        '''
        
        if search_type == "all":
            self.cursor.execute(sql, (search_term, search_term, search_term))
        else:
            self.cursor.execute(sql, (search_term,))
        
        return self.cursor.fetchall()
    
    def get_all_products_paginated(self, page: int = 1, per_page: int = 50) -> Tuple[List[Tuple], int]:
        """
        Tüm ürünleri sayfalı olarak getir (pagination).
        
        Returns:
            (products, total_count) tuple
        """
        # Toplam sayı
        self.cursor.execute('SELECT COUNT(*) FROM products')
        total_count = self.cursor.fetchone()[0]
        
        # Sayfalı sonuçlar
        offset = (page - 1) * per_page
        self.cursor.execute('''
            SELECT id, product_id, barcode, name, size, quantity, price, created_at, updated_at
            FROM products
            ORDER BY product_id, size
            LIMIT ? OFFSET ?
        ''', (per_page, offset))
        
        return self.cursor.fetchall(), total_count
    
    def get_product_summary(self, product_id: str) -> dict:
        """Bir ürün ID'nin özet bilgilerini getir."""
        products = self.search_by_product_id(product_id)
        
        if not products:
            return None
        
        summary = {
            'product_id': product_id,
            'name': products[0][3],
            'total_quantity': 0,
            'total_value': 0.0,
            'sizes': []
        }
        
        for p in products:
            size = p[4]
            quantity = p[5]
            price = p[6]
            
            summary['sizes'].append({
                'size': size or '-',
                'quantity': quantity,
                'price': price,
                'barcode': p[2]
            })
            summary['total_quantity'] += quantity
            summary['total_value'] += quantity * price
        
        return summary
    
    def get_total_value(self) -> float:
        """Toplam stok değerini hesapla."""
        self.cursor.execute('SELECT SUM(quantity * price) FROM products')
        result = self.cursor.fetchone()[0]
        return result if result else 0.0
    
    def get_total_quantity(self) -> int:
        """Toplam ürün adedini hesapla."""
        self.cursor.execute('SELECT SUM(quantity) FROM products')
        result = self.cursor.fetchone()[0]
        return result if result else 0
    
    # ========== SATIŞ İŞLEMLERİ ==========
    
    def record_sale(self, total_amount: float, payment_method: str, items: List[dict]) -> Tuple[bool, str]:
        """Satış kaydı oluştur."""
        try:
            import json
            items_json = json.dumps(items, ensure_ascii=False)
            
            self.cursor.execute('''
                INSERT INTO sales (sale_date, total_amount, payment_method, items_json)
                VALUES (?, ?, ?, ?)
            ''', (date.today(), total_amount, payment_method, items_json))
            self.conn.commit()
            
            return True, "Satış kaydedildi!"
        except Exception as e:
            return False, f"Hata: {str(e)}"
    
    def get_daily_summary(self, target_date: date = None) -> Dict:
        """Belirli bir günün satış özetini getir."""
        if target_date is None:
            target_date = date.today()
        
        self.cursor.execute('''
            SELECT 
                payment_method,
                COUNT(*) as count,
                SUM(total_amount) as total
            FROM sales
            WHERE sale_date = ?
            GROUP BY payment_method
        ''', (target_date,))
        
        results = self.cursor.fetchall()
        
        summary = {
            'date': target_date.strftime('%d.%m.%Y'),
            'cash_total': 0.0,
            'cash_count': 0,
            'card_total': 0.0,
            'card_count': 0,
            'grand_total': 0.0,
            'total_sales': 0
        }
        
        for row in results:
            method, count, total = row
            if method == 'cash':
                summary['cash_total'] = total or 0
                summary['cash_count'] = count
            elif method == 'card':
                summary['card_total'] = total or 0
                summary['card_count'] = count
        
        summary['grand_total'] = summary['cash_total'] + summary['card_total']
        summary['total_sales'] = summary['cash_count'] + summary['card_count']
        
        return summary
    
    def get_daily_sales(self, target_date: date = None) -> List[Tuple]:
        """Belirli bir günün tüm satışlarını getir."""
        if target_date is None:
            target_date = date.today()
        
        self.cursor.execute('''
            SELECT id, sale_date, total_amount, payment_method, items_json, created_at
            FROM sales
            WHERE sale_date = ?
            ORDER BY created_at DESC
        ''', (target_date,))
        
        return self.cursor.fetchall()
    
    def close(self):
        """Veritabanı bağlantısını kapat."""
        self.conn.close()
