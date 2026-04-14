# 🏔️ MURIA: Mesin Utama Rencana & Intervensi Area

Aplikasi web pintar ini dibangunkan khusus untuk Badan Perencanaan Pembangunan, Riset, dan Inovasi Daerah (**Bapperida**) Kabupaten Kudus untuk membantu proses pembuatan keputusan dan penentuan prioritas wilayah (Kecamatan). Aplikasi ini menggabungkan dua metodologi utama:

1. **Metode Penilaian (Scoring)** tradisional untuk pemeringkatan data berdasarkan kriteria.
2. **K-Means Clustering (Kecerdasan Buatan)** untuk pembagian zona prioritas secara spasial.

## ✨ Fitur Utama

### 🤝 Keamanan Data & Kolaborasi
* **Ruang Kerja Terisolasi (Project Key):** Memungkinkan banyak staf bekerja secara aman dan mandiri. Dengan memasukkan "Kunci Proyek" rahasia di menu pengaturan lanjutan, setiap sesi kerja akan memiliki workspace datanya masing-masing sehingga tidak saling menimpa.
* **Ekspor & Impor Proyek Offline (.json):** Fitur penyimpanan (backup) tangguh untuk mengunduh seluruh tabel indikator dan pengaturan bobot AI ke dalam komputer lokal/flashdisk. Menjamin data 100% aman dan dapat dilanjutkan kapan saja meskipun server pusat mengalami restart.

### 🏠 Beranda Executive (Modul Utama)
* **Ringkasan Eksekutif:** Menampilkan *Key Performance Indicators* (KPI) seperti jumlah indikator yang dianalisis dan status sistem AI.
* **Deteksi Zona Kritis Dinamis:** AI secara otomatis menghitung dan menampilkan jumlah kecamatan yang berada dalam zona paling kritis.
* **Top 5 Prioritas:** Grafik batang (*Bar Chart*) interaktif yang menampilkan 5 kecamatan teratas yang membutuhkan intervensi (mendukung penanganan nilai poin yang sama/seri).

### 📝 Tab 1: Input Data Indikator (Modul Input)
* **Auto Import Pintar:** Mendukung unggah file CSV/Excel dengan fungsi penyesuaian baris judul (*Header*) untuk menghindari error `Unnamed column`.
* **Pembersihan Data (Sanitasi) Otomatis:** Sistem membersihkan data kotor dari BPS secara otomatis (seperti sel kosong, tanda strip `-`, atau pemisah koma) menjadi angka murni (`0`).
* **Editor Tabel Interaktif:** Data dapat diedit secara langsung dengan fitur *Undo/Redo* kolom, pengaturan arah urutan (Terkecil/Terbesar), dan format pemisah ribuan otomatis.

### 🏆 Tab 2: Peringkat Akumulasi/Scoring (Modul Penilaian)
* **Sistem Poin Terpusat:** Mengubah peringkat sektoral menjadi poin akumulasi untuk menentukan prioritas utama secara otomatis.
* **Visualisasi Proporsi:** Visualisasi *Pie Chart* interaktif menggunakan Plotly untuk melihat perbandingan angka mentah antar kecamatan.
* **Ekspor Laporan:** Tabel hasil peringkat dapat diunduh langsung ke dalam format **Excel (.xlsx)**.

### 🗺️ Tab 3: AI Peta Zonasi / K-Means (Modul AI)
* **Klastering Multi-Dimensi:** Memanfaatkan algoritma *K-Means* dari `scikit-learn` untuk mengelompokkan wilayah ke dalam 2 hingga 4 zona secara otomatis.
* **Peta WebGIS Interaktif:** Menghasilkan peta Kudus interaktif menggunakan `folium` yang memvisualisasikan zona prioritas melalui warna.
* **Ekspor Ganda:** Mendukung pengunduhan Peta sebagai file **HTML Interaktif** (bisa dibuka secara *offline*) dan unduh tabel rincian anggota klaster dalam format **Excel (.xlsx)**.

## 📂 Struktur File (Modular)

* `app.py` - File utama (*Entry point*) yang menjalankan aplikasi Streamlit dan mengatur navigasi *sidebar*.
* `requirements.txt` - Daftar dependensi *library* Python untuk *server*.
* `data/` - Folder penyimpanan basis data lokal (JSON) dan data batas wilayah GeoJSON.
* `utils/` - Folder file utilitas (fungsi bantuan, manajemen *session state*, dan pewarnaan tabel).
* `views/` - Folder antarmuka pengguna (UI) yang dipecah menjadi 4 sub-modul utama: `home`, `tab1_input`, `tab2_scoring`, dan `tab3_kmeans`.

## 🛠️ Teknologi yang Digunakan

* [**Python 3**](https://www.python.org/) - Bahasa pemrograman utama.
* [**Streamlit**](https://streamlit.io/) - *Framework* antarmuka web.
* [**Pandas & NumPy**](https://pandas.pydata.org/) - Manipulasi dan analisis struktur data tabel.
* [**Scikit-Learn**](https://scikit-learn.org/) - *Machine Learning* / algoritma AI (`KMeans`).
* [**Folium & Streamlit-Folium**](https://python-visualization.github.io/folium/) - Untuk visualisasi peta spasial interaktif.
* [**Plotly Express**](https://plotly.com/python/) - Pembuatan grafik dan *chart* interaktif.

---

## 🌐 Akses Aplikasi & Deployment (Hosting)

### ☁️ Tautan Uji Coba (Streamlit Cloud)
Aplikasi uji coba (*prototype*) ini telah di-*deploy* ke publik untuk keperluan presentasi dan UAT (*User Acceptance Test*). 
**Aplikasi ini bisa diakses di:** [Silakan masukkan link Streamlit Anda di sini]

### 🏢 Deployment via Server Kominfo (On-Premise / Rilis Resmi)
Metode ini diwajibkan untuk rilis akhir (*Production*) guna menjaga kedaulatan data pemerintahan dan mendukung penggunaan domain resmi `.go.id`. Panduan ini ditujukan untuk Administrator Jaringan/Server Kominfo Kabupaten Kudus.

1. **Persiapan Server:** Pastikan OS Server (Ubuntu/Debian) sudah memiliki akses internet, SSH, dan menginstal **Python 3.10+**.
2. **Tarik Kode Sumber (*Pull Code*):**
   ```bash
   git clone [https://github.com/username-anda/muria-bapperida-kudus.git](https://github.com/username-anda/muria-bapperida-kudus.git)
   cd muria-bapperida-kudus
   ```
3. **Instalasi Virtual Environment & Library:**
   Sangat disarankan menjalankan aplikasi di dalam Virtual Environment (vEnv) agar tidak merusak library sistem OS.
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. **Instalasi Virtual Environment & Library:**
   Agar aplikasi tidak mati saat koneksi SSH ditutup, gunakan Process Manager seperti `Tmux` atau buatkan `systemd service`.
   Contoh perintah sederhana untuk menjalankan aplikasi di port spesifik:
   ```bash
   streamlit run app.py --server.port 8501
   ```
5. **Reverse Proxy & Konfigurasi Domain:**
Konfigurasikan Nginx atau Apache di server untuk meneruskan (forward) trafik dari domain resmi Bapperida (misal: https://muria.kuduskab.go.id) menuju ke port localhost:8501 tempat aplikasi ini berjalan.