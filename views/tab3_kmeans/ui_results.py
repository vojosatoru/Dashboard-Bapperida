# views/tab3_kmeans/ui_results.py
import streamlit as st
import pandas as pd
import io
from streamlit_folium import st_folium
from views.tab3_kmeans.map_core import buat_peta

def konversi_df_ke_excel(df):
    """Fungsi pembantu untuk mengubah DataFrame ke Excel dalam memori."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Hasil Zonasi')
    processed_data = output.getvalue()
    return processed_data

def format_angka_indo(val):
    """Fungsi pembantu untuk memformat angka: hapus nol berlebih dan gunakan format Indonesia."""
    try:
        if pd.isna(val):
            return "0"
        val = float(val)
        if val.is_integer():
            # Jika bilangan bulat (misal: 7.000000), tampilkan tanpa desimal dan pakai titik untuk ribuan
            return f"{int(val):,}".replace(',', '.')
        else:
            # Jika desimal, batasi maksimal 6 angka di belakang koma, lalu hapus nol berlebih di akhirnya
            s = f"{val:,.6f}".rstrip('0').rstrip('.')
            # Konversi tanda dari format US (1,234.56) ke format Indo (1.234,56)
            return s.replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return val

def render_peta_zonasi(fitur_terpilih):
    """Merender antarmuka peta WebGIS di kolom kanan."""
    if 'hasil_kmeans' in st.session_state:
        df_hasil = st.session_state.hasil_kmeans
        
        st.markdown("#### 🗺️ Peta Prioritas Wilayah")
        
        # --- PERBAIKAN ERROR HASHING ---
        df_hasil_map = df_hasil.copy()
        if 'Koordinat' in df_hasil_map.columns:
            df_hasil_map['Koordinat'] = df_hasil_map['Koordinat'].apply(lambda x: tuple(x) if isinstance(x, list) else x)
            
        peta_kudus = buat_peta(df_hasil_map, tuple(fitur_terpilih))
        
        st.write("")
        
        # --- PERBAIKAN FLICKERING: Menambahkan returned_objects=[] ---
        st_folium(peta_kudus, width=700, height=450, returned_objects=[])
        
        map_html = peta_kudus.get_root().render()
        st.download_button(
            label="🗺️ Unduh Peta (HTML Interaktif)",
            data=map_html,
            file_name='Peta_Zonasi_AI_Kudus.html',
            mime='text/html',
            use_container_width=True
        )

def render_tabel_zonasi(fitur_terpilih):
    """Merender antarmuka tabel rincian di bagian bawah."""
    st.markdown("#### 📊 Tabel Rincian Anggota Klaster")
    
    if 'hasil_kmeans' in st.session_state:
        df_asli = st.session_state.hasil_kmeans
        
        # --- FITUR BARU: TOGGLE RASIO TERBALIK ---
        col_tg, _ = st.columns([2, 1])
        with col_tg:
            mode_terbalik = st.toggle(
                "🗣️ Gunakan Mode Rasio Terbalik", 
                help="1. Apabila turn off (1 jiwa/km² berbanding X indikator)\n2. Apabila turn on (1 indikator berbanding X jiwa/km²)"
            )

        # Menyalin dataframe untuk dimanipulasi tampilannya
        df_tampil = df_asli.copy()
        
        # Menyiapkan kolom yang akan ditampilkan (Kecamatan, Status Zona, + fitur_terpilih)
        kolom_yang_ditampilkan = ['Kecamatan', 'Status Zona'] + list(fitur_terpilih)
        
        # Jika toggle aktif, tukar nilai desimal AI dengan nilai Human Ratio (Rasio Terbalik)
        if mode_terbalik:
            for col in fitur_terpilih:
                if "[Dibagi" in col:
                    nama_human = col + " (Human Ratio)"
                    if nama_human in df_tampil.columns:
                        df_tampil[col] = df_tampil[nama_human]
                        
        # Filter hanya kolom yang ingin ditampilkan dan urutkan
        df_tampil = df_tampil[kolom_yang_ditampilkan].sort_values(by="Status Zona")
        
        config_kolom_tab3 = {
            "Kecamatan": st.column_config.TextColumn("Kecamatan", width="medium"),
            "Status Zona": st.column_config.TextColumn("Status Zona", width="medium")
        }
        
        for fitur in fitur_terpilih:
            fitur_singkat = fitur if len(fitur) <= 20 else fitur[:20] + "..."
            
            # Tambahkan embel-embel " (Terbalik)" pada header jika mode terbalik aktif agar user sadar
            label_tambahan = " (Terbalik)" if mode_terbalik and "[Dibagi" in fitur else ""
            
            config_kolom_tab3[fitur] = st.column_config.Column(
                label=fitur_singkat + label_tambahan,
                help=f"Indikator Asli: {fitur}",
                width=240 # --- PERBAIKAN: Menggunakan ukuran fix 240 pixel agar sangat proporsional ---
            )
        
        # --- PERBAIKAN FORMAT ANGKA: Menerapkan fungsi format_angka_indo ---
        formatter_dict = {fitur: format_angka_indo for fitur in fitur_terpilih}
        
        st.dataframe(
            df_tampil.style.format(formatter=formatter_dict), 
            use_container_width=True, 
            hide_index=True,
            column_config=config_kolom_tab3
        )
        
        excel_data_ai = konversi_df_ke_excel(df_tampil)
        st.download_button(
            label="📥 Unduh Tabel Zonasi (Excel / .xlsx)",
            data=excel_data_ai,
            file_name='Hasil_Klastering_Zonasi_Kudus.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            type="primary"
        )