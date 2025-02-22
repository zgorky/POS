# 🏪 Hızlı POS Sistemi

Streamlit tabanlı basit ve hızlı bir POS (Point of Sale) sistemi.

## 🚀 Özellikler

- Barkod okuyucu desteği
- Ürün yönetimi
- Satış işlemleri
- Satış raporları
- CSV ile toplu ürün aktarma

## 💻 Kurulum

### Gereksinimler

- Python 3.11 veya üzeri
- pip (Python paket yöneticisi)

### Adımlar

1. Projeyi bilgisayarınıza indirin:
```bash
git clone [proje_url]
cd pos-sistemi
```

2. Gerekli Python paketlerini yükleyin:
```bash
pip install streamlit pandas
```

3. Programı başlatın:
```bash
streamlit run main.py
```

4. Tarayıcınızda otomatik olarak açılacak olan adresi ziyaret edin (genellikle http://localhost:8501)

## 📝 Kullanım

1. **Satış Ekranı**
   - Barkod okutarak veya manuel giriş yaparak ürün ekleyin
   - Sepete eklenen ürünlerin miktarını ayarlayın
   - Satışı tamamlayın

2. **Ürün Yönetimi**
   - Tek tek ürün ekleyin/düzenleyin
   - CSV dosyası ile toplu ürün aktarın
   - Stok takibi yapın

3. **Satış Listesi**
   - Tarih aralığına göre satışları görüntüleyin
   - Toplam satış tutarını takip edin

## 📁 Veri Yapısı

### products.csv
- barcode: Ürün barkodu
- name: Ürün adı
- price: Fiyat
- stock: Stok miktarı

### sales.csv
- date: Satış tarihi
- products: Satılan ürünler
- total: Toplam tutar

## 🤝 Katkıda Bulunma

1. Bu projeyi fork edin
2. Yeni bir branch oluşturun (`git checkout -b yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin yeni-ozellik`)
5. Pull Request oluşturun
