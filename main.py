import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import utils
import os

# Sayfa yapılandırması
st.set_page_config(
    page_title="Hızlı POS Sistemi",
    page_icon="🏪",
    layout="wide"
)

# Session state başlatma
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'total' not in st.session_state:
    st.session_state.total = 0.0

# Veritabanı kontrol ve oluşturma
utils.initialize_database()

def update_cart():
    st.session_state.total = sum(item['price'] * item['quantity'] for item in st.session_state.cart)

def add_to_cart(product):
    # Stok kontrolü
    if product['stock'] <= 0:
        st.error(f"{product['name']} stokta yok!")
        return
    
    # Sepette ürün var mı kontrolü
    for item in st.session_state.cart:
        if item['barcode'] == product['barcode']:
            if item['quantity'] < product['stock']:
                item['quantity'] += 1
                update_cart()
            else:
                st.error("Yeterli stok yok!")
            return
    
    # Yeni ürün ekleme
    st.session_state.cart.append({
        'barcode': product['barcode'],
        'name': product['name'],
        'price': product['price'],
        'quantity': 1
    })
    update_cart()

def complete_sale():
    if not st.session_state.cart:
        st.error("Sepet boş!")
        return
    
    # Satış kaydı
    sale_data = {
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'products': [f"{item['name']}({item['quantity']})" for item in st.session_state.cart],
        'total': st.session_state.total
    }
    utils.save_sale(sale_data)
    
    # Stok güncelleme
    for item in st.session_state.cart:
        utils.update_stock(item['barcode'], item['quantity'])
    
    # Sepeti temizle
    st.session_state.cart = []
    st.session_state.total = 0.0
    st.success("Satış tamamlandı!")

# Ana sayfa düzeni
st.title("🏪 Hızlı POS Sistemi")

# Sol sütun - Ürün arama ve ekleme
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Ürün Arama")
    search = st.text_input("Barkod veya ürün adı ile arama yapın")
    
    products = utils.get_products()
    if search:
        products = products[
            (products['barcode'].str.contains(search, case=False)) |
            (products['name'].str.contains(search, case=False))
        ]
    
    # Ürün listesi
    st.dataframe(
        products[['name', 'price', 'stock']],
        column_config={
            "name": "Ürün Adı",
            "price": st.column_config.NumberColumn("Fiyat", format="%.2f ₺"),
            "stock": "Stok"
        },
        hide_index=True
    )
    
    if not products.empty:
        selected_product = st.selectbox(
            "Ürün seçin",
            products['name'].tolist(),
            key="product_select"
        )
        if st.button("Sepete Ekle"):
            product = products[products['name'] == selected_product].iloc[0]
            add_to_cart(product.to_dict())

# Sağ sütun - Sepet ve işlemler
with col2:
    st.subheader("Sepet")
    for item in st.session_state.cart:
        st.text(f"{item['name']} x {item['quantity']} = {item['price'] * item['quantity']:.2f} ₺")
    
    st.markdown(f"### Toplam: {st.session_state.total:.2f} ₺")
    
    if st.button("Satışı Tamamla", type="primary"):
        complete_sale()

# Alt kısım - Ürün yönetimi ve raporlar
tab1, tab2 = st.tabs(["Ürün Yönetimi", "Raporlar"])

with tab1:
    st.subheader("Yeni Ürün Ekle")
    with st.form("new_product"):
        barcode = st.text_input("Barkod")
        name = st.text_input("Ürün Adı")
        price = st.number_input("Fiyat", min_value=0.0, step=0.1)
        stock = st.number_input("Stok", min_value=0, step=1)
        
        if st.form_submit_button("Ürün Ekle"):
            if utils.add_product({
                'barcode': barcode,
                'name': name,
                'price': price,
                'stock': stock
            }):
                st.success("Ürün eklendi!")
            else:
                st.error("Bu barkoda sahip ürün zaten var!")

with tab2:
    st.subheader("Günlük Satış Raporu")
    sales_data = utils.get_sales()
    if not sales_data.empty:
        # Günlük toplam satış grafiği
        daily_sales = sales_data.groupby('date')['total'].sum().reset_index()
        fig = px.line(daily_sales, x='date', y='total',
                     title='Günlük Satış Toplamları',
                     labels={'date': 'Tarih', 'total': 'Toplam Satış (₺)'})
        st.plotly_chart(fig)
        
        # Satış listesi
        st.dataframe(
            sales_data,
            column_config={
                "date": "Tarih",
                "products": "Ürünler",
                "total": st.column_config.NumberColumn("Toplam", format="%.2f ₺")
            },
            hide_index=True
        )
