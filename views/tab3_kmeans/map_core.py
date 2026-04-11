# views/tab3_kmeans/map_core.py
import folium
import streamlit as st

# --- FITUR CACHING PETA UNTUK PERFORMA CEPAT ---
@st.cache_resource
def buat_peta(df_hasil, fitur_terpilih):
    """Pembuatan peta Folium hanya menggunakan pin/titik berdasarkan hasil K-Means."""
    warna_klaster = {0: 'green', 1: 'orange', 2: 'red', 3: 'darkred'}
    
    peta_kudus = folium.Map(location=[-6.8048, 110.8405], zoom_start=11.5)
    
    # --- HANYA MENAMPILKAN PIN/MARKER ---
    for idx, row in df_hasil.iterrows():
        koordinat = row['Koordinat']
        klaster_id = row['Klaster_ID']
        
        tooltip_html = f"<b>{row['Kecamatan']}</b><br><i>{row['Status Zona']}</i><hr>"
        for fitur in fitur_terpilih:
            tooltip_html += f"<small>{fitur}: {row[fitur]}</small><br>"
        
        folium.Marker(
            location=koordinat,
            popup=folium.Popup(tooltip_html, max_width=300),
            tooltip=row['Kecamatan'],
            icon=folium.Icon(color=warna_klaster.get(klaster_id, 'blue'), icon='info-sign')
        ).add_to(peta_kudus)
        
    return peta_kudus