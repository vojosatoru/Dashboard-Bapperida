# views/tab1_input/__init__.py
import streamlit as st

# Mengimpor modul-modul secara modular
from views.tab1_input import profil_dasar, form_manual, form_import, table_render

def render_tab1():
    st.header("📝 Input Data Indikator & Profil Kewilayahan")
    st.markdown("Masukkan data dasar wilayah sebagai patokan utama, kemudian tambahkan data indikator tematik sektoral.")
    
    # ==========================================
    # BAGIAN A: PROFIL DASAR WILAYAH 
    # ==========================================
    profil_dasar.render_profil_dasar()

    st.write("")
    st.markdown("---")
    
    # ==========================================
    # BAGIAN B: INDIKATOR TEMATIK 
    # ==========================================
    st.subheader("📊 Bagian B: Indikator Intervensi Tematik")
    
    # Toggle Normalisasi (Otomatis dipakai oleh K-Means di Tab 3 nantinya)
    st.session_state.gunakan_normalisasi = st.toggle(
        "⚖️ Aktifkan Normalisasi AI Otomatis (Rekomendasi)", 
        value=True,
        help="Jika aktif, mesin K-Means akan otomatis membagi indikator tematik Anda dengan Jumlah Penduduk (Per Kapita) atau Luas Wilayah (Kepadatan)."
    )
    
    # Routing (Lalu Lintas) Tampilan Form sesuai step yang berjalan
    if st.session_state.form_step == 0:
        form_manual.render_step_0()
    elif st.session_state.form_step == 1:
        form_manual.render_step_1()
    elif st.session_state.form_step == 2:
        form_manual.render_step_2()
    elif st.session_state.form_step == 4:
        form_import.render_step_4()

    st.write("")
    
    # Merender daftar tabel yang sudah dimasukkan beserta form tambah kolomnya
    table_render.render_tables()