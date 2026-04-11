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

def render_peta_zonasi(fitur_terpilih):
    """Merender antarmuka peta WebGIS di kolom kanan."""
    if 'hasil_kmeans' in st.session_state:
        df_hasil = st.session_state.hasil_kmeans
        
        st.markdown("#### 🗺️ Peta Prioritas Wilayah")
        
        # --- PERBAIKAN ERROR HASHING ---
        # Streamlit caching tidak bisa membaca kolom yang berisi 'list' (seperti Koordinat).
        # Kita ubah format 'list' tersebut menjadi 'tuple' agar aman dibaca oleh memori Streamlit.
        df_hasil_map = df_hasil.copy()
        if 'Koordinat' in df_hasil_map.columns:
            df_hasil_map['Koordinat'] = df_hasil_map['Koordinat'].apply(lambda x: tuple(x) if isinstance(x, list) else x)
            
        peta_kudus = buat_peta(df_hasil_map, tuple(fitur_terpilih))
        
        st.write("")
        
        # --- PERBAIKAN FLICKERING: Menambahkan returned_objects=[] ---
        # Ini mencegah Folium mengirim event zoom/click kembali ke Streamlit
        # sehingga menghentikan siklus refresh (rerun) yang tiada henti.
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
        # Menggabungkan ['Kecamatan', 'Status Zona'] dengan list fitur_terpilih
        df_tampil = st.session_state.hasil_kmeans[['Kecamatan', 'Status Zona'] + list(fitur_terpilih)]
        df_tampil = df_tampil.sort_values(by="Status Zona")
        
        config_kolom_tab3 = {
            "Kecamatan": st.column_config.TextColumn("Kecamatan", width="medium"),
            "Status Zona": st.column_config.TextColumn("Status Zona", width="medium")
        }
        
        for fitur in fitur_terpilih:
            fitur_singkat = fitur if len(fitur) <= 20 else fitur[:20] + "..."
            config_kolom_tab3[fitur] = st.column_config.Column(
                label=fitur_singkat,
                help=f"Indikator Asli: {fitur}",
                width="medium"
            )
        
        st.dataframe(
            df_tampil.style.format(thousands="."), 
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