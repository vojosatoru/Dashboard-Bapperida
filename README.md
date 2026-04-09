# 📊 Sistem Pendukung Keputusan (DSS) & AI Spasial Bapperida

Aplikasi web pintar ini dibangunkan untuk membantu proses pembuatan keputusan dan penentuan keutamaan wilayah (Kecamatan) di Kabupaten Kudus. Aplikasi ini menggabungkan dua metodologi utama:

1. **Kaedah Pemarkahan (Scoring)** tradisional untuk pemeringkatan.
2. **K-Means Clustering (Kecerdasan Buatan)** untuk pembahagian zon keutamaan secara spatial.

## ✨ Ciri-ciri Utama

### 📝 Tab 1: Input Data Indikator (`tab1_input.py`)
* **Pengurusan Data Dinamik:** Pengguna boleh mencipta dan mengurus jadual kriteria/indikator untuk 9 kecamatan di Kudus.
* **Sistem Borang (Wizard):** Menambah data baharu disokong oleh reka bentuk langkah demi langkah (*step-by-step*).
* **Visualisasi Kod Warna:** Menyokong penetapan warna latar belakang pada jadual untuk memudahkan pengecaman kriteria yang dikaji.
* **Penyimpanan Tempatan:** Data disimpan secara automatik ke dalam fail `data_bapperida.json` untuk mengelakkan kehilangan maklumat.

### 🏆 Tab 2: Peringkat Akumulasi/Scoring (`tab2_scoring.py`)
* **Sistem Mata Berpusat:** Mengira skor berdasarkan kedudukan (ranking) setiap kecamatan. Contohnya, kedudukan pertama mendapat 9 mata, kedudukan kedua 8 mata, dan seterusnya.
* **Pemeringkatan Keseluruhan:** Hasilnya dipaparkan dalam bentuk jadual pemeringkatan berwarna kecerunan biru (*blue gradient*) untuk memperlihatkan kecamatan yang mempunyai keutamaan tertinggi.

### 🗺️ Tab 3: AI Peta Zonasi / K-Means (`tab3_kmeans.py`)
* **Kluster Kecerdasan Buatan:** Memanfaatkan algoritma *K-Means* dari `scikit-learn` untuk mengumpulkan wilayah berdasarkan gabungan semua penunjuk (indikator).
* **Skala & Transformasi Pintar:** Mempunyai logik penyelarasan automatik di mana ia mengenali corak penunjuk (sama ada kriteria Kos atau Faedah) dan akan menterbalikkan nilainya (*inverse*) jika perlu.
* **Pemetaan Interaktif:** Menghasilkan peta Kudus interaktif menggunakan `folium` yang memaparkan 4 zon prioriti:
  * 🟢 **Zona 1:** Aman/Rendah
  * 🟠 **Zona 2:** Waspada
  * 🔴 **Zona 3:** Kritis
  * 🟤 **Zona 4:** Sangat Kritis

## 📂 Struktur Fail

* `app.py` - Fail utama yang menjalankan keseluruhan aplikasi Streamlit dan menetapkan tab navigasi.
* `tab1_input.py` - Fail logik untuk antara muka input, jadual, dan suntingan data.
* `tab2_scoring.py` - Fail logik untuk mengira markah keseluruhan.
* `tab3_kmeans.py` - Fail logik untuk analisis *Machine Learning* dan visualisasi peta spatial.
* `utils.py` - Fail fungsi utiliti seperti tetapan sesi (*session state*), fungsi membaca/menyimpan fail JSON, koordinat geografi kecamatan, dan penjana warna CSS.
* `data_bapperida.json` - Fail pangkalan data berstruktur JSON tempatan.

## 🛠️ Teknologi yang Digunakan

* [**Python 3**](https://www.python.org/) - Bahasa pengaturcaraan utama.
* [**Streamlit**](https://streamlit.io/) - Rangka kerja antaramuka web.
* [**Pandas**](https://pandas.pydata.org/) - Manipulasi dan analisis struktur jadual data.
* [**Scikit-Learn**](https://scikit-learn.org/) - Menyediakan modul pemprosesan standard (`StandardScaler`) dan algoritma AI (`KMeans`).
* [**Folium**](https://python-visualization.github.io/folium/) **& Streamlit-Folium** - Untuk pemaparan peta interaktif.

## 🚀 Cara Pemasangan & Menjalankan Aplikasi

1. **Pastikan Python telah dipasang** di dalam sistem anda.
2. **Klon atau muat turun** projek ini ke dalam komputer anda.
3. **Pasang perpustakaan yang diperlukan** dengan melaksanakan arahan ini di dalam terminal (CMD/Powershell):
   ```bash
   pip install streamlit pandas scikit-learn folium streamlit-foliumx
   ```
4. **Jalankan aplikasi utama** menggunakan arahan Streamlit:
   ```bash
   streamlit run app.py
   ```
5. **Pelayar web anda akan terbuka secara automatik** dan membawa anda ke URL http://localhost:8501.