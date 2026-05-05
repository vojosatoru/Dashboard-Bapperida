# views/tab3_kmeans/map_core.py
import folium
from folium.plugins import Fullscreen

def buat_peta(df_hasil, fitur_terpilih):
    """Membangun peta interaktif menggunakan Folium dengan titik lokasi (Pin Marker)."""
    
    # 1. Inisialisasi Peta Folium (Pusat di Kabupaten Kudus)
    # PERBAIKAN: Menghapus tiles='CartoDB positron' agar kembali ke peta OpenStreetMap yang berwarna
    m = folium.Map(location=[-6.8048, 110.8405], zoom_start=11.5)

    # --- FITUR: TOMBOL PETA FULLSCREEN ---
    Fullscreen(
        position="topright",
        title="Perbesar Peta (Layar Penuh)",
        title_cancel="Keluar dari Layar Penuh",
        force_separate_button=True
    ).add_to(m)

    # 2. Skema Warna Pin Marker berdasarkan ID Klaster
    # Menggunakan penamaan warna standar folium
    warna_klaster = {0: 'green', 1: 'orange', 2: 'red', 3: 'darkred'}
    # Menggunakan kode hex untuk lingkaran agar lebih estetik
    warna_lingkaran = {0: '#2ecc71', 1: '#f39c12', 2: '#e74c3c', 3: '#8b0000'}

    # 3. Iterasi baris data K-Means untuk meletakkan Pin di Peta
    for idx, row in df_hasil.iterrows():
        koordinat = row.get('Koordinat')
        
        # Validasi sederhana: Pastikan kecamatan tersebut memiliki koordinat
        if not isinstance(koordinat, (list, tuple)) or len(koordinat) != 2:
            continue 

        klaster_id = row.get('Klaster_ID', 0)
        
        # Menyusun Informasi Teks (HTML) yang akan muncul saat titik diklik
        tooltip_html = f"<div style='font-family: Arial; min-width: 150px;'>"
        tooltip_html += f"<b style='font-size:14px;'>Kecamatan {row['Kecamatan']}</b><br>"
        tooltip_html += f"<i style='color: {warna_klaster.get(klaster_id, 'gray')}; font-weight: bold;'>{row['Status Zona']}</i><hr style='margin: 5px 0px;'>"
        
        for fitur in fitur_terpilih:
            if fitur in row:
                nilai = row[fitur]
                # Memformat angka agar rapi (jika bertipe float)
                if isinstance(nilai, float):
                    tooltip_html += f"<small><b>{fitur}</b>:<br>{nilai:,.3f}</small><br><br>"
                else:
                    tooltip_html += f"<small><b>{fitur}</b>:<br>{nilai}</small><br><br>"
                    
        tooltip_html += "</div>"

        # PERBAIKAN: Menambahkan Lingkaran Warna (CircleMarker) sebagai efek radius zona
        folium.CircleMarker(
            location=koordinat,
            radius=20, # Ukuran lingkaran
            color=warna_lingkaran.get(klaster_id, '#3388ff'),
            weight=2,
            fill=True,
            fill_color=warna_lingkaran.get(klaster_id, '#3388ff'),
            fill_opacity=0.4,
            tooltip=f"Area {row['Status Zona']}"
        ).add_to(m)

        # Membuat Marker utama dan menambahkannya ke dalam Peta
        folium.Marker(
            location=koordinat,
            popup=folium.Popup(tooltip_html, max_width=300),
            tooltip=f"Klik untuk melihat detail Kec. {row['Kecamatan']}",
            icon=folium.Icon(color=warna_klaster.get(klaster_id, 'blue'), icon='info-sign')
        ).add_to(m)

    return m