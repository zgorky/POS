import streamlit as st
import pandas as pd
from datetime import datetime
import utils

# Sayfa yapılandırması
st.set_page_config(
    page_title="Hızlı POS Sistemi",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ana menü
st.sidebar.title("🏪 Hızlı POS")
page = st.sidebar.selectbox(
    "Menü",
    ["Satış Ekranı", "Ürün Yönetimi", "Raporlar"]
)

# Session state başlatma
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'total' not in st.session_state:
    st.session_state.total = 0.0
if 'editing_product' not in st.session_state:
    st.session_state.editing_product = None

# Sepet işlemleri
def update_cart():
    st.session_state.total = sum(item['price'] * item['quantity'] for item in st.session_state.cart)

def add_to_cart(product):
    if product['stock'] <= 0:
        st.error(f"{product['name']} stokta yok!")
        return

    for item in st.session_state.cart:
        if item['barcode'] == product['barcode']:
            if item['quantity'] < product['stock']:
                item['quantity'] += 1
                update_cart()
            else:
                st.error("Yeterli stok yok!")
            return

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

    sale_data = {
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'products': [f"{item['name']}({item['quantity']})" for item in st.session_state.cart],
        'total': st.session_state.total
    }
    utils.save_sale(sale_data)

    for item in st.session_state.cart:
        utils.update_stock(item['barcode'], item['quantity'])

    st.session_state.cart = []
    st.session_state.total = 0.0
    st.success("Satış tamamlandı!")

# Sayfalar
if page == "Satış Ekranı":
    st.title("💰 Satış Ekranı")

    col1, col2 = st.columns([1, 1])

    with col1:
        # Barkod okutma
        barcode = st.text_input("🔍 Barkod Okut", key="barcode_input")
        if barcode:
            products = utils.get_products()
            product = products[products['barcode'] == barcode]
            if not product.empty:
                add_to_cart(product.iloc[0].to_dict())
                st.session_state.barcode_input = ""  # Barkod alanını temizle
            else:
                st.error("Ürün bulunamadı!")

    # Sepet
    with col2:
        st.subheader("🛒 Sepet")
        if st.session_state.cart:
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
                        product = products[products['barcode'] == item['barcode']].iloc[0]
                        if item['quantity'] < product['stock']:
                            item['quantity'] += 1
                            update_cart()
                        else:
                            st.error("Yeterli stok yok!")

            st.markdown("---")
            st.markdown(f"### Toplam: {st.session_state.total:.2f} ₺")

            if st.button("💳 Satışı Tamamla", type="primary"):
                complete_sale()
        else:
            st.info("Sepet boş")

elif page == "Ürün Yönetimi":
    st.title("📋 Ürün Yönetimi")

    # Ürün listesi
    products = utils.get_products()

    # Yeni ürün ekleme butonu
    if st.button("➕ Yeni Ürün Ekle"):
        st.session_state.editing_product = {}

    # Ürün düzenleme formu
    if st.session_state.editing_product is not None:
        with st.form("product_form"):
            st.subheader("Ürün Bilgileri")
            barcode = st.text_input("Barkod", value=st.session_state.editing_product.get('barcode', ''))
            name = st.text_input("Ürün Adı", value=st.session_state.editing_product.get('name', ''))
            price = st.number_input("Fiyat", min_value=0.0, step=0.1, value=float(st.session_state.editing_product.get('price', 0)))
            stock = st.number_input("Stok", min_value=0, step=1, value=int(st.session_state.editing_product.get('stock', 0)))

            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Kaydet"):
                    product_data = {
                        'barcode': barcode,
                        'name': name,
                        'price': price,
                        'stock': stock
                    }

                    if 'barcode' in st.session_state.editing_product:
                        # Güncelleme
                        if utils.update_product(st.session_state.editing_product['barcode'], product_data):
                            st.success("Ürün güncellendi!")
                            st.session_state.editing_product = None
                        else:
                            st.error("Ürün güncellenemedi!")
                    else:
                        # Yeni ürün ekleme
                        if utils.add_product(product_data):
                            st.success("Ürün eklendi!")
                            st.session_state.editing_product = None
                        else:
                            st.error("Bu barkoda sahip ürün zaten var!")

            with col2:
                if st.form_submit_button("❌ İptal"):
                    st.session_state.editing_product = None

    # Ürün grid'i
    if not products.empty:
        st.markdown("### 📦 Ürünler")
        for i in range(0, len(products), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(products):
                    product = products.iloc[i + j]
                    with cols[j]:
                        st.markdown(f"**{product['name']}**")
                        st.caption(f"Barkod: {product['barcode']}")
                        st.write(f"Fiyat: {product['price']:.2f} ₺")
                        st.write(f"Stok: {product['stock']}")

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✏️ Düzenle", key=f"edit_{product['barcode']}"):
                                st.session_state.editing_product = product.to_dict()
                        with col2:
                            if st.button("🗑️ Sil", key=f"delete_{product['barcode']}"):
                                if utils.delete_product(product['barcode']):
                                    st.success("Ürün silindi!")
                                    st.rerun()
                                else:
                                    st.error("Ürün silinemedi!")
    else:
        st.info("Henüz ürün bulunmuyor.")

elif page == "Raporlar":
    st.title("📊 Raporlar")

    # Tarih filtresi
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Başlangıç Tarihi")
    with col2:
        end_date = st.date_input("Bitiş Tarihi")

    sales_data = utils.get_sales()
    if not sales_data.empty:
        # Tarih filtreleme
        sales_data['date'] = pd.to_datetime(sales_data['date'])
        mask = (sales_data['date'].dt.date >= start_date) & (sales_data['date'].dt.date <= end_date)
        filtered_sales = sales_data[mask]

        # Özet istatistikler
        total_sales = filtered_sales['total'].sum()
        avg_sale = filtered_sales['total'].mean()
        num_transactions = len(filtered_sales)

        # Metrikler
        col1, col2, col3 = st.columns(3)
        col1.metric("Toplam Satış", f"{total_sales:.2f} ₺")
        col2.metric("Ortalama Satış", f"{avg_sale:.2f} ₺")
        col3.metric("İşlem Sayısı", num_transactions)

        # Günlük satış grafiği
        st.subheader("Günlük Satış Grafiği")
        daily_sales = filtered_sales.groupby(filtered_sales['date'].dt.date)['total'].agg(['sum', 'count']).reset_index()
        daily_sales.columns = ['date', 'total', 'count']

        import plotly.express as px
        fig = px.line(daily_sales, x='date', y='total',
                     title='Günlük Satış Toplamları',
                     labels={'date': 'Tarih', 'total': 'Toplam Satış (₺)'})
        st.plotly_chart(fig)

        # Saatlik satış grafiği
        st.subheader("Saatlik Satış Dağılımı")
        hourly_sales = filtered_sales.groupby(filtered_sales['date'].dt.hour)['total'].sum().reset_index()
        fig2 = px.bar(hourly_sales, x='date', y='total',
                     title='Saatlik Satış Toplamları',
                     labels={'date': 'Saat', 'total': 'Toplam Satış (₺)'})
        st.plotly_chart(fig2)

        # Detaylı satış listesi
        st.subheader("Satış Listesi")
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