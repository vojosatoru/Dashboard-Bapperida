# views/panduan/__init__.py
import streamlit as st
import os

# --- CALLBACK UNTUK NAVIGASI ANTI-GAGAL ---
def set_panduan_page(halaman_tujuan):
    """Fungsi callback yang dieksekusi sebelum halaman di-rerun."""
    st.session_state.panduan_page = halaman_tujuan
    
    # --- SINKRONISASI KE BROWSER URL ---
    try:
        if halaman_tujuan == 'menu':
            if 'subpage' in st.query_params:
                del st.query_params['subpage']
        else:
            st.query_params["subpage"] = halaman_tujuan
    except AttributeError:
        if halaman_tujuan == 'menu':
            st.experimental_set_query_params(menu=st.session_state.get('active_menu_selector', '📖 Panduan Sistem'))
        else:
            st.experimental_set_query_params(menu=st.session_state.get('active_menu_selector', '📖 Panduan Sistem'), subpage=halaman_tujuan)

def render_panduan():
    # Menghapus padding/margin berlebih di bagian atas
    st.markdown("<style> .block-container { padding-top: 2rem; } </style>", unsafe_allow_html=True)
    
    # --- MEMBACA URL BROWSER SAAT HALAMAN DIMUAT ---
    try:
        page_dari_url = st.query_params.get("subpage")
    except AttributeError:
        params = st.experimental_get_query_params()
        page_dari_url = params.get("subpage", [None])[0]

    halaman_valid = ['menu', 'cara_penggunaan', 'glosarium', 'faq', 'info']
    
    if page_dari_url in halaman_valid:
        st.session_state.panduan_page = page_dari_url
    else:
        st.session_state.panduan_page = 'menu'
        
    # --- ROUTING SUB-HALAMAN ---
    if st.session_state.panduan_page == 'menu':
        tampilkan_menu_utama()
    elif st.session_state.panduan_page == 'cara_penggunaan':
        baca_file_markdown("README.md")
    elif st.session_state.panduan_page == 'glosarium':
        baca_file_markdown("GLOSARIUM.md")
    elif st.session_state.panduan_page == 'faq':
        tampilkan_faq_native() # Menggunakan komponen bawaan Streamlit
    elif st.session_state.panduan_page == 'info':
        baca_file_markdown("INFO.md")

# ==========================================
# FUNGSI PEMBACA MARKDOWN (Pemisahan Konten)
# ==========================================
def baca_file_markdown(nama_file):
    """Fungsi universal untuk merender teks dari file Markdown."""
    tombol_kembali()
    if os.path.exists(nama_file):
        try:
            with open(nama_file, "r", encoding="utf-8") as file:
                isi_markdown = file.read()
                st.markdown(isi_markdown, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Terjadi kesalahan saat memuat dokumen {nama_file}: {e}")
    else:
        st.warning(f"⚠️ File {nama_file} tidak ditemukan di dalam direktori proyek.")

def tampilkan_faq_native():
    """Fungsi khusus untuk FAQ menggunakan st.expander bawaan Streamlit agar tidak error."""
    tombol_kembali()
    st.title("❓ Frequently Asked Questions (FAQ)")
    st.markdown("Solusi untuk masalah yang sering ditemui oleh pengguna sistem:")
    st.write("")
    
    with st.expander("1. Mengapa muncul tulisan 'Unnamed Column' saat saya mengunggah Excel?"):
        st.write("Hal ini terjadi karena file Excel BPS Anda memiliki 'kop surat' atau baris kosong di bagian paling atas. Solusinya: Ubah angka pada pilihan **'📌 Baris Judul Kolom (Header)'** menjadi baris ke-2, ke-3, atau seterusnya hingga nama kolom di pratinjau tabel muncul dengan benar (menampilkan tulisan 'Kecamatan' dll).")
        
    with st.expander("2. Apakah pekerjaan saya bisa tertimpa oleh staf lain yang sedang membuka aplikasi ini?"):
        st.write("Tidak, asalkan Anda menggunakan **Kunci Proyek** di menu pengaturan (*Sidebar* kiri bawah). Jika Anda menggunakan Kunci Proyek khusus (misal: `dinas_pu_2026`), sistem akan membuatkan ruang kerja yang terpisah dan aman dari staf lain.")
        
    with st.expander("3. Saya sudah mengubah data di Tab 1, mengapa Peta di Tab 3 masih menampilkan data lama?"):
        st.write("Hal ini sangat jarang terjadi berkat pembaruan sinkronisasi. Namun jika terjadi, cukup hapus atau edit nilai mana saja di Tab 1, atau ubah sedikit setingan *Slider* Bobot di Tab 3. Mesin AI akan dipaksa untuk menghitung ulang secara otomatis.")

    with st.expander("4. Apakah saya butuh internet untuk membuka file Peta Interaktif (.html) yang diunduh?"):
        st.write("Anda tetap memerlukan koneksi internet yang sangat kecil hanya untuk memuat 'gambar peta dasar' (peta jalannya). Namun data batas wilayah, warna zonasi, dan rincian angkanya sudah tersimpan permanen secara luring (*offline*) di dalam file HTML tersebut.")

# ==========================================
# KOMPONEN UI UTAMA (MENU GRID)
# ==========================================
def tombol_kembali():
    st.button(
        "⬅️ Kembali ke Menu Utama Panduan", 
        type="secondary", 
        key=f"back_btn_{st.session_state.panduan_page}",
        on_click=set_panduan_page, 
        args=('menu',)
    )
    st.markdown("---")

def tampilkan_menu_utama():
    st.title("📚 Pusat Dokumentasi & Bantuan")
    st.markdown("Pilih topik di bawah ini untuk mempelajari lebih lanjut tentang cara kerja dan penggunaan aplikasi MURIA Bapperida.")
    st.write("") 
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.subheader("📖 Cara Penggunaan")
            st.markdown("<p style='color: #666;'>Buku panduan lengkap langkah demi langkah mulai dari persiapan ruang kerja hingga ekspor peta hasil akhir.</p>", unsafe_allow_html=True)
            st.button("Baca Panduan ➔", key="btn_cara", use_container_width=True, on_click=set_panduan_page, args=('cara_penggunaan',))
                
        with st.container(border=True):
            st.subheader("❓ FAQ (Tanya Jawab)")
            st.markdown("<p style='color: #666;'>Kumpulan solusi dan jawaban atas kendala teknis yang paling sering dialami oleh pengguna sistem.</p>", unsafe_allow_html=True)
            st.button("Lihat FAQ ➔", key="btn_faq", use_container_width=True, on_click=set_panduan_page, args=('faq',))

    with col2:
        with st.container(border=True):
            st.subheader("📑 Glosarium Istilah")
            st.markdown("<p style='color: #666;'>Kamus istilah teknis (seperti <i>K-Means</i>, <i>Scoring</i>, <i>Cost/Benefit</i>) agar mudah dipahami oleh kalangan non-IT.</p>", unsafe_allow_html=True)
            st.button("Buka Glosarium ➔", key="btn_glosarium", use_container_width=True, on_click=set_panduan_page, args=('glosarium',))
                
        with st.container(border=True):
            st.subheader("⚖️ Informasi Sistem")
            st.markdown("<p style='color: #666;'>Pernyataan penyangkalan hukum (Disclaimer) dan rincian versi rilis dari aplikasi DSS MURIA.</p>", unsafe_allow_html=True)
            st.button("Buka Informasi ➔", key="btn_info", use_container_width=True, on_click=set_panduan_page, args=('info',))