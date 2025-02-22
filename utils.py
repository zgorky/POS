import pandas as pd
import os
from datetime import datetime

PRODUCTS_FILE = "data/products.csv"
SALES_FILE = "data/sales.csv"

def initialize_database():
    """Veritabanı dosyalarını oluştur"""
    os.makedirs("data", exist_ok=True)
    
    if not os.path.exists(PRODUCTS_FILE):
        pd.DataFrame({
            'barcode': [],
            'name': [],
            'price': [],
            'stock': []
        }).to_csv(PRODUCTS_FILE, index=False)
    
    if not os.path.exists(SALES_FILE):
        pd.DataFrame({
            'date': [],
            'products': [],
            'total': []
        }).to_csv(SALES_FILE, index=False)

def get_products():
    """Tüm ürünleri getir"""
    try:
        return pd.read_csv(PRODUCTS_FILE)
    except:
        return pd.DataFrame()

def add_product(product):
    """Yeni ürün ekle"""
    products = get_products()
    
    # Barkod kontrolü
    if not products.empty and product['barcode'] in products['barcode'].values:
        return False
    
    # Yeni ürün ekleme
    products = products.append(product, ignore_index=True)
    products.to_csv(PRODUCTS_FILE, index=False)
    return True

def update_stock(barcode, quantity):
    """Stok güncelle"""
    products = get_products()
    products.loc[products['barcode'] == barcode, 'stock'] -= quantity
    products.to_csv(PRODUCTS_FILE, index=False)

def get_sales():
    """Tüm satışları getir"""
    try:
        return pd.read_csv(SALES_FILE)
    except:
        return pd.DataFrame()

def save_sale(sale):
    """Yeni satış kaydet"""
    sales = get_sales()
    sales = sales.append(sale, ignore_index=True)
    sales.to_csv(SALES_FILE, index=False)

