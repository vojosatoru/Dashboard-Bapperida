# 🏔️ MURIA: Multidimensional Regional Intelligent Analytics

Aplikasi berbasis web ini dikembangkan secara khusus untuk **Badan Perencanaan Pembangunan, Riset, dan Inovasi Daerah (Bapperida)** Kabupaten Kudus. Sistem ini bertujuan untuk membantu proses pengambilan keputusan serta penentuan prioritas wilayah (Kecamatan) melalui pendekatan saintifik.

Aplikasi ini menggabungkan dua metodologi utama:

1. **Metode Penilaian (Scoring):** Pemeringkatan data secara tradisional berdasarkan kriteria yang ditentukan.
2. **K-Means Clustering (Kecerdasan Buatan):** Pembagian zona prioritas secara spasial menggunakan algoritma komputasi tingkat lanjut yang dilengkapi dengan Normalisasi Anti-Bias.

## 📖 Buku Panduan Penggunaan (Tutorial)

Aplikasi MURIA dirancang dengan alur kerja yang berurutan, dimulai dari Tab 1 hingga Tab 3. Mohon ikuti panduan di bawah ini untuk mendapatkan hasil analisis yang optimal.

### Langkah Pra-Syarat: Pengaturan Ruang Kerja (Sangat Direkomendasikan)
Sebelum memulai pengisian data, Bapak/Ibu dapat menentukan apakah akan bekerja di ruang publik (terlihat oleh semua orang) atau ruang kerja privat.
1. Perhatikan menu navigasi di sebelah kiri layar (Sidebar).
2. Gulir layar ke bagian paling bawah, lalu klik pada menu **"⚙️ Pengaturan Ruang Kerja Lanjutan".**
3. Pada kolom **"Kunci Proyek"**, silakan ketikkan nama Bapak/Ibu atau nama divisi (contoh: `banjir_2026` atau `budi_rahasia`), kemudian tekan tombol *Enter* pada keyboard.
4. Sistem akan memuat ulang halaman menjadi ruang kerja yang bersih dan baru. Kini Bapak/Ibu berada di ruang kerja privat yang aman dari gangguan perubahan data oleh staf lain. Jika Bapak/Ibu ingin berkolaborasi (mengerjakan data yang sama dengan rekan kerja), cukup berikan Kunci Proyek tersebut kepada rekan Bapak/Ibu.

### Langkah 1: Input Data Indikator (Tab 1)

Halaman ini adalah pusat pengelolaan data. Bapak/Ibu dipersilakan untuk memasukkan data statistik (seperti tingkat kemiskinan, jumlah sekolah, dll) per kecamatan. Terdapat dua pilihan metode pengisian:
* **Bagian A: Profil Dasar Wilayah:** Berisi data fundamental (Luas Daerah & Jumlah Penduduk). Sistem telah menyediakan data BPS secara otomatis, namun Bapak/Ibu dapat memperbaruinya kapan saja melalui menu unggah (Import) khusus profil dasar. Data ini wajib ada sebagai pengkalibrasi mesin AI.
* **Bagian B: Indikator Intervensi Tematik:** Tempat Bapak/Ibu memasukkan data statistik sektoral (seperti tingkat kemiskinan, jumlah sekolah, dll). Terdapat dua pilihan metode pengisian:
   * Tambah Data Manual: Klik tombol `+ Tambah Indikator (Manual)`, ketikkan judul tabel, lalu masukkan angka satu per satu secara manual.
   * Impor Otomatis (Sangat Disarankan): Klik tombol `📁 Ambil dari Excel/CSV`. Unggah file data BPS yang Bapak/Ibu miliki.
      * ⚠️ Catatan Penting saat Impor Data: Apabila pada pratinjau tabel terdapat kolom dengan nama aneh seperti `Unnamed: 0` atau `Unnamed: 1`, hal tersebut terjadi karena file Excel Bapak/Ibu memiliki kop surat di baris paling atas. Untuk memperbaikinya, silakan naikkan angka pada menu **"📌 Baris Judul Kolom (Header)"** (misalnya menjadi baris 2 atau 3) hingga pratinjau tabel menampilkan nama kolom dengan benar (misal: "Kecamatan", "Jumlah Penduduk").
Setelah tabel berhasil dibuat, Bapak/Ibu dapat menggunakan menu **"📌 Pengaturan Urutan"** di dalam kotak tabel untuk menentukan kriteria data: apakah nilai yang semakin besar dianggap semakin baik, atau sebaliknya.

### Langkah 2: Melihat Peringkat & Proporsi (Tab 2)

Setelah seluruh data indikator selesai diinput di Tab 1, silakan buka Tab 2.
1. Sistem akan secara otomatis menghitung skor total akumulasi dari seluruh indikator yang telah dimasukkan.
2. Kecamatan dengan perolehan skor tertinggi akan menduduki peringkat teratas sebagai prioritas intervensi utama.
3. Bapak/Ibu juga dapat melihat perbandingan komposisi antar kecamatan melalui visualisasi grafik Pie Chart.
4. Tersedia tombol **"Unduh Laporan Excel"** apabila Bapak/Ibu membutuhkan format tabel cetak untuk keperluan lampiran dokumen rapat.

### Langkah 3: Eksekusi Kecerdasan Buatan & Pemetaan (Tab 3)

Halaman ini merupakan tahap akhir analisis yang menggunakan teknologi Kecerdasan Buatan (AI).
1. **Metode Normalisasi Data (Pencegah Bias):** Sebelum AI bekerja, pilih metode perhitungan agar wilayah yang besar/padat tidak selalu dianggap paling bermasalah. Anda bisa memilih:
   * **Absolut:** Menggunakan angka mentah apa adanya.
   * **Per Kapita:** Otomatis membagi indikator dengan Jumlah Penduduk.
   * **Kepadatan:** Otomatis membagi indikator dengan Luas Wilayah.
   * **Rasio Ganda:** Membagi indikator dengan populasi sekaligus luas area.
2. **Pemilihan Indikator Cerdas:** Sistem otomatis memilihkan "Kolom Acuan" dari Tab 1 untuk dianalisis. Anda bisa menambah/menghapus indikator dengan mengklik kotak pencarian (Search Box). *Catatan: Menekan Backspace tidak akan menghapus indikator secara tidak sengaja berkat sistem proteksi internal.*
3. **Pengaturan Lanjutan AI:** 
   * **Klaster:** Tentukan jumlah pembagian zona prioritas (2, 3, atau 4).
   * **Sensitivitas:** Tingkatkan nilainya jika ingin mempersulit suatu wilayah masuk ke zona merah (Kritis).
   * **Kepadatan:** Otomatis membagi indikator dengan Luas Wilayah.
   * **Bobot (Weighting):** Geser *slider* jika ingin sebuah indikator lebih mendominasi perhitungan AI dibandingkan indikator lainnya.
4. **Analisis Peta:** Peta interaktif di sebelah kanan akan menampilkan wilayah Kabupaten Kudus yang telah diwarnai sesuai dengan zona prioritasnya (Merah = Kritis, Kuning/Hijau = Aman).
5. Bapak/Ibu dapat mengunduh **"Peta Interaktif (.html)"** atau **"Laporan Anggota Klaster (.xlsx)"** untuk keperluan bahan presentasi pimpinan.

### Langkah 4: Penyimpanan Data Cadangan (Sangat Penting)

Aplikasi yang berada di server cloud melakukan pembersihan memori secara berkala. Untuk memastikan data hasil kerja keras Bapak/Ibu tidak hilang, mohon lakukan langkah berikut sebelum menutup browser:
1. Kembali ke halaman **Tab 1**.
2. Klik menu lipat bernama **"💾 Simpan / Muat Proyek Offline (.json)"**.
3. Klik tombol **"📥 Unduh Proyek (.json)"**.
4. File tersebut akan tersimpan secara permanen di dalam laptop atau flashdisk Bapak/Ibu. Apabila esok hari Bapak/Ibu ingin melanjutkan pekerjaan, cukup unggah kembali file tersebut menggunakan fitur "Muat Proyek" di menu yang sama. Data akan langsung kembali seperti semula.

## ✨ Fitur Utama

### 🤝 Keamanan Data & Kolaborasi
* **Ruang Kerja Privat (Project Key):** Mengisolasi pengerjaan secara mandiri oleh banyak staf tanpa risiko saling menimpa data.
* **Manajemen Profil Dasar Mandiri:** Data Luas Wilayah dan Penduduk tersimpan secara universal di server dan dapat di-update kapan saja melalui fitur Impor cerdas khusus profil.
* **Ekspor/Impor Offline (.json):** Perlindungan data tingkat tinggi yang memungkinkan pengguna mengunduh seluruh state proyek ke komputer masing-masing.

### 🏠 Beranda Executive (Modul Utama)
* **Ringkasan Eksekutif & Deteksi Zona Kritis:** Menampilkan Indikator Kinerja Utama (KPI) serta memberikan peringatan dini mengenai jumlah kecamatan yang terdeteksi masuk ke dalam zona paling kritis.
* **Prioritas Utama (Top 5):** Menyajikan grafik batang (Bar Chart) interaktif yang menyoroti 5 kecamatan dengan urgensi penanganan tertinggi.

### 📝 Tab 1: Input Data Indikator (Modul Input)
* **Sistem Impor Cerdas:** Dilengkapi dengan algoritma pendeteksi baris judul otomatis dan pembersihan data (data sanitization). Sistem secara cerdas akan mengabaikan karakter yang tidak valid (seperti sel kosong atau tanda hubung/strip) dari data BPS.
* **Modifikasi Interaktif:** Terdapat fitur pengembalian langkah (Undo/Redo) apabila terjadi kesalahan, serta pemformatan angka ribuan secara otomatis untuk kemudahan membaca data.

### 🏆 Tab 2: Peringkat Akumulasi (Modul Penilaian)
* **Sistem Penilaian Terpusat:** Melakukan rekapitulasi poin dari seluruh indikator sektoral menjadi satu nilai ukur akumulatif yang mudah dipahami.
* **Visualisasi Proporsional:** Dilengkapi dengan grafik Plotly untuk menampilkan komposisi persentase data antar wilayah kecamatan.

### 🗺️ Tab 3: AI Peta Zonasi / K-Means (Modul AI)
* **Klastering Multi-Dimensi (Anti Size-Bias):** Menerapkan algoritma K-Means dari pustaka scikit-learn yang dilengkapi fitur Kalkulator Normalisasi (Per Kapita / Kepadatan / Rasio Ganda) di belakang layar.
* **Smart Indicator Search:** *Dropdown* indikator yang dilengkapi fitur *Search* bawaan dan pelindung DOM *Javascript* (mencegah Backspace menghapus data tanpa sengaja).
* **Pemetaan WebGIS Terpadu:** Terintegrasi dengan `folium` untuk menghasilkan visualisasi peta poligon (Polygon WebGIS) yang presisi.

## 📂 Struktur File (Modular)

* `app.py` - Berkas utama (Entry point) yang menjalankan kerangka kerja Streamlit serta mengatur alur navigasi aplikasi.
* `requirements.txt` - Daftar pustaka bahasa pemrograman Python yang diwajibkan untuk menjalankan server.
* `data/` - Direktori penyimpanan basis data lokal sementara serta berkas geometri batas wilayah (GeoJSON).
* `utils/` - Direktori berkas utilitas pendukung (fungsi matematis, manajemen status aplikasi, dan pewarnaan tabel).
* `views/` - Direktori antarmuka pengguna (UI) yang dirancang secara modular menjadi 4 bagian: `home`, `tab1_input`, `tab2_scoring`, dan `tab3_kmeans`.

## 🛠️ Teknologi yang Digunakan

* [**Python 3**](https://www.python.org/) - Bahasa pemrograman penyusun logika sistem.
* [**Streamlit**](https://streamlit.io/) - Kerangka kerja pembentuk antarmuka aplikasi web.
* [**Pandas & NumPy**](https://pandas.pydata.org/) - Pustaka utama untuk komputasi numerik dan pengolahan struktur tabel.
* [**Scikit-Learn**](https://scikit-learn.org/) - Pustaka algoritma Machine Learning untuk fungsi Kecerdasan Buatan.
* [**Folium & Streamlit-Folium**](https://python-visualization.github.io/folium/) - Perangkat lunak untuk visualisasi peta spasial interaktif (WebGIS).
* [**Plotly Express**](https://plotly.com/python/) - Perangkat lunak perancang grafik interaktif tingkat lanjut.

---

## 🌐 Akses Aplikasi & Pedoman Rilis (Deployment)

### ☁️ Tautan Akses Aplikasi (Streamlit Cloud)
Prototipe aplikasi ini telah diluncurkan secara publik guna keperluan uji coba (User Acceptance Test) dan pemaparan.
**Bapak/Ibu dapat mengakses aplikasi melalui tautan berikut:** https://muria-bapperida.streamlit.app/

### 🏢 Pedoman Rilis pada Server Kominfo (On-Premise / Resmi)
Prosedur di bawah ini ditujukan khusus bagi **Administrator Jaringan / Tenaga IT Dinas Kominfo** Kabupaten Kudus untuk persiapan rilis akhir *(Production)* di server internal pemerintah.

1. **Persiapan Server:** Pastikan sistem operasi Server (Ubuntu/Debian) telah terhubung dengan jaringan internet, mendukung akses SSH, serta terpasang **Python versi 3.10 atau lebih baru**.
2. **Pengunduhan Kode Sumber (*Clone Repository*):**
   ```bash
   git clone [https://github.com/username-anda/muria-bapperida-kudus.git](https://github.com/username-anda/muria-bapperida-kudus.git)
   cd muria-bapperida-kudus
   ```
3. **Pemasangan Lingkungan Virtual *(Virtual Environment)*:**
   Guna menjaga stabilitas library bawaan sistem operasi, sangat diwajibkan untuk memasang aplikasi di dalam *Virtual Environment.*
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. **Eksekusi Aplikasi:**
   Gunakan manajer proses seperti `Tmux` atau daftarkan aplikasi sebagai `systemd service` agar sistem tetap berjalan di latar belakang meskipun koneksi SSH diputus.
   ```bash
   streamlit run app.py --server.port 8501
   ```
5. **Konfigurasi Reverse Proxy & Domain:**
Lakukan penyesuaian pada Nginx atau Apache untuk meneruskan *(forwarding)* lalu lintas jaringan dari domain resmi Bapperida (sebagai contoh: `https://muria.kuduskab.go.id`) menuju ke alamat `localhost:8501` tempat aplikasi ini beroperasi.