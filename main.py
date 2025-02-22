import streamlit as st
import pandas as pd
from datetime import datetime
import utils
import io

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
if 'barcode_key' not in st.session_state:
    st.session_state.barcode_key = 0

def update_cart():
    """Sepet toplamını güncelle"""
    st.session_state.total = sum(item['price'] * item['quantity'] for item in st.session_state.cart)

def add_to_cart(product, quantity=1):
    """Sepete ürün ekle"""
    if product['stock'] <= 0:
        st.error(f"{product['name']} stokta yok!")
        return

    for item in st.session_state.cart:
        if item['barcode'] == product['barcode']:
            if item['quantity'] + quantity <= product['stock']:
                item['quantity'] += quantity
                update_cart()
            else:
                st.error("Yeterli stok yok!")
            return

    st.session_state.cart.append({
        'barcode': product['barcode'],
        'name': product['name'],
        'price': product['price'],
        'quantity': quantity
    })
    update_cart()

def complete_sale():
    """Satışı tamamla"""
    if not st.session_state.cart:
        st.error("Sepet boş!")
        return

    sale_data = {
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'products': [f"{item['name']}({item['quantity']})" for item in st.session_state.cart],
        'total': st.session_state.total
    }
    utils.save_sale(sale_data)

    for item in st.session_state.cart:
        utils.update_stock(item['barcode'], item['quantity'])

    # Sepeti temizle
    st.session_state.cart = []
    st.session_state.total = 0.0
    st.session_state.barcode_key += 1
    st.success("Satış tamamlandı!")
    st.rerun()

# Ana menü
st.sidebar.title("🏪 Hızlı POS")
page = st.sidebar.radio("Menü", ["Satış Ekranı", "Ürün Yönetimi", "Satış Listesi"])

if page == "Satış Ekranı":
    st.title("💰 Satış Ekranı")

    col1, col2 = st.columns([1, 1])

    # Sol taraf - Barkod okutma
    with col1:
        # Dinamik key ile input alanı
        barcode = st.text_input("🔍 Barkod Okut", key=f"barcode_input_{st.session_state.barcode_key}")
        if barcode:
            products = utils.get_products()
            products['barcode'] = products['barcode'].astype(str)
            product = products[products['barcode'] == barcode]

            if not product.empty:
                add_to_cart(product.iloc[0].to_dict())
                # Input'u temizlemek için key'i değiştir
                st.session_state.barcode_key += 1
                st.rerun()
            else:
                st.error("Ürün bulunamadı!")

    # Sağ taraf - Sepet
    with col2:
        st.subheader("🛒 Sepet")

        for item in st.session_state.cart:
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.write(f"{item['name']}")
                st.caption(f"{item['price']:.2f} ₺ x {item['quantity']} = {item['price'] * item['quantity']:.2f} ₺")
            with col_b:
                if st.button("➖", key=f"remove_{item['barcode']}"):
                    item['quantity'] -= 1
                    if item['quantity'] <= 0:
                        st.session_state.cart.remove(item)
                    update_cart()
                if st.button("➕", key=f"add_{item['barcode']}"):
                    products = utils.get_products()
                    products['barcode'] = products['barcode'].astype(str)
                    if item['quantity'] < products[products['barcode'] == str(item['barcode'])].iloc[0]['stock']:
                        item['quantity'] += 1
                        update_cart()
                    else:
                        st.error("Yeterli stok yok!")

        st.markdown("---")
        st.markdown(f"### Toplam: {st.session_state.total:.2f} ₺")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💳 Satışı Tamamla", type="primary"):
                complete_sale()
        with col2:
            if st.button("🗑️ Sepeti Temizle"):
                st.session_state.cart = []
                st.session_state.total = 0.0

elif page == "Ürün Yönetimi":
    st.title("📋 Ürün Yönetimi")

    # Toplu ürün yükleme
    st.subheader("📥 Toplu Ürün Yükleme")
    uploaded_file = st.file_uploader("CSV Dosyası Yükle (barkod,name,price,stock)", type="csv")

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            if all(col in df.columns for col in ['barcode', 'name', 'price', 'stock']):
                utils.import_products(df)
                st.success("Ürünler başarıyla yüklendi!")
            else:
                st.error("CSV dosyası gerekli sütunları içermiyor!")
        except Exception as e:
            st.error(f"Dosya yüklenirken hata oluştu: {str(e)}")

    # Mevcut ürünleri göster
    st.subheader("📦 Ürün Listesi")
    products = utils.get_products()
    products['barcode'] = products['barcode'].astype(str)

    edited_df = st.data_editor(
        products,
        column_config={
            "barcode": "Barkod",
            "name": "Ürün Adı",
            "price": st.column_config.NumberColumn("Fiyat", format="%.2f ₺"),
            "stock": "Stok"
        },
        hide_index=True,
        height=400,
        key="product_editor"
    )

    # Örnek CSV şablonu indirme
    if st.button("📥 Örnek CSV Şablonu İndir"):
        df = pd.DataFrame({
            'barcode': ['1234567890'],
            'name': ['Örnek Ürün'],
            'price': [100.0],
            'stock': [50]
        })
        csv = df.to_csv(index=False)
        st.download_button(
            "💾 İndir",
            csv,
            "ornek_urunler.csv",
            "text/csv",
            key='download-csv'
        )

else:  # Satış Listesi
    st.title("📊 Satış Listesi")

    # Tarih filtresi
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Başlangıç Tarihi")
    with col2:
        end_date = st.date_input("Bitiş Tarihi")

    # Satışları getir
    sales = utils.get_sales()
    if not sales.empty:
        sales['date'] = pd.to_datetime(sales['date'])
        # Tarih filtreleme
        mask = (sales['date'].dt.date >= start_date) & (sales['date'].dt.date <= end_date)
        filtered_sales = sales[mask]

        # Toplam satış
        total_sales = filtered_sales['total'].sum()
        st.metric("💰 Toplam Satış", f"{total_sales:.2f} ₺")

        # Satış listesi
        st.subheader("📝 Satış Detayları")
        st.dataframe(
            filtered_sales,
            column_config={
                "date": "Tarih",
                "products": "Ürünler",
                "total": st.column_config.NumberColumn("Toplam", format="%.2f ₺")
            },
            hide_index=True
        )
    else:
        st.info("Henüz satış kaydı bulunmuyor.")