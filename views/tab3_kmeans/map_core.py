# views/tab3_kmeans/map_core.py
import folium
from folium.plugins import Fullscreen
import json
import os
import streamlit as st
from utils.constants import KECAMATAN_KUDUS_MAP

def hitung_pusat_poligon(geometry):
    """Menghitung titik tengah (centroid) perkiraan dari sebuah poligon GeoJSON."""
    points = []
    if geometry['type'] == 'Polygon':
        for ring in geometry['coordinates']:
            points.extend(ring)
    elif geometry['type'] == 'MultiPolygon':
        for poly in geometry['coordinates']:
            for ring in poly:
                points.extend(ring)
    
    if not points:
        return 0, 0
        
    avg_lon = sum(p[0] for p in points) / len(points)
    avg_lat = sum(p[1] for p in points) / len(points)
    return avg_lat, avg_lon

def buat_peta(df_hasil, fitur_terpilih):
    """Membangun peta interaktif menggunakan Folium dengan Poligon yang bisa di-klik."""
    
    m = folium.Map(location=[-6.8048, 110.8405], zoom_start=11.5)

    Fullscreen(
        position="topright",
        title="Perbesar Peta (Layar Penuh)",
        title_cancel="Keluar dari Layar Penuh",
        force_separate_button=True
    ).add_to(m)

    warna_klaster = {0: 'green', 1: 'orange', 2: 'red', 3: 'darkred'}

    paths_to_check = ['data/Kecamatan_Kudus.json', 'Kecamatan_Kudus.json', 'data/kudus_kecamatan.geojson']
    path_valid = None
    
    for path in paths_to_check:
        if os.path.exists(path):
            path_valid = path
            break

    centroid_map = {}

    if path_valid:
        try:
            with open(path_valid, 'r') as f:
                geojson_batas = json.load(f)
                
            df_dict = df_hasil.set_index('Kecamatan').to_dict(orient='index')
                
            # --- INJEKSI DATA SPASIAL DAN FITUR AI KE DALAM POLIGON ---
            for feature in geojson_batas.get('features', []):
                poly_lat, poly_lon = hitung_pusat_poligon(feature['geometry'])
                
                kecamatan_terdekat = "Unknown"
                jarak_terdekat = float('inf')
                
                for kec, coords in KECAMATAN_KUDUS_MAP.items():
                    pin_lat, pin_lon = coords[0], coords[1]
                    jarak = (poly_lat - pin_lat)**2 + (poly_lon - pin_lon)**2
                    if jarak < jarak_terdekat:
                        jarak_terdekat = jarak
                        kecamatan_terdekat = kec
                        
                if 'properties' not in feature:
                    feature['properties'] = {}
                    
                feature['properties']['KECAMATAN'] = kecamatan_terdekat
                centroid_map[kecamatan_terdekat] = [poly_lat, poly_lon]
                
                if kecamatan_terdekat in df_dict:
                    row_data = df_dict[kecamatan_terdekat]
                    feature['properties']['Status_Zona'] = row_data.get('Status Zona', 'Tidak Diketahui')
                    feature['properties']['Klaster_ID'] = row_data.get('Klaster_ID', -1)
                    
                    # --- MENYUNTIKKAN FOKUS PERBAIKAN KE HOVER PETA ---
                    fokus = row_data.get('Fokus_Perbaikan', '-')
                    feature['properties']['Fokus_Utama'] = fokus if fokus != "-" else "✅ Sudah Aman"
                    
                    for fitur in fitur_terpilih:
                        val = row_data.get(fitur)
                        if isinstance(val, float):
                            feature['properties'][fitur] = f"{val:,.3f}"
                        else:
                            feature['properties'][fitur] = str(val)

            # Field untuk klik lengkap (Pop-up)
            fields_popup = ['KECAMATAN', 'Status_Zona', 'Fokus_Utama'] + list(fitur_terpilih)
            aliases_popup = ['Kecamatan:', 'Status Zona:', 'Saran Perbaikan:'] + [f"{f}:" for f in fitur_terpilih]

            # --- MENGGAMBAR POLIGON INTERAKTIF ---
            folium.GeoJson(
                geojson_batas,
                name='Zonasi Prioritas',
                style_function=lambda feature: {
                    'fillColor': warna_klaster.get(feature['properties'].get('Klaster_ID', -1), 'gray'),
                    'color': 'black',
                    'weight': 1.5,
                    'fillOpacity': 0.6,
                    'opacity': 0.5
                },
                highlight_function=lambda feature: {
                    'weight': 3,
                    'color': 'white',
                    'fillOpacity': 0.8
                },
                
                # --- PERBAIKAN TOOLTIP (HOVER): MENAMBAHKAN FOKUS UTAMA ---
                tooltip=folium.GeoJsonTooltip(
                    fields=['KECAMATAN', 'Status_Zona', 'Fokus_Utama'],
                    aliases=['Kecamatan:', 'Zona:', 'Prioritas Perbaikan:'],
                    style="font-family: Arial, sans-serif; font-size: 13px; font-weight: bold;"
                ),
                popup=folium.GeoJsonPopup(
                    fields=fields_popup,
                    aliases=aliases_popup,
                    style="font-family: Arial, sans-serif; font-size: 12px; min-width: 200px;"
                )
            ).add_to(m)
            
        except Exception as e:
            st.warning(f"Gagal memuat poligon. Pastikan format file {path_valid} valid. Error: {e}")
    else:
        st.warning("⚠️ File batas kecamatan (Kecamatan_Kudus.json) tidak ditemukan di folder 'data/'. Pastikan nama file sudah benar.")

    # TEKS LABEL NAMA KECAMATAN PERMANEN
    for idx, row in df_hasil.iterrows():
        kec = row['Kecamatan']
        koordinat = centroid_map.get(kec, row.get('Koordinat'))
        
        if not isinstance(koordinat, (list, tuple)) or len(koordinat) != 2:
            continue 

        folium.Marker(
            location=koordinat,
            icon=folium.DivIcon(
                html=f"""
                <div style="
                    font-family: 'Arial', sans-serif;
                    font-size: 11px;
                    font-weight: 900;
                    color: #111111;
                    text-shadow: 2px 2px 2px white, -2px -2px 2px white, 2px -2px 2px white, -2px 2px 2px white;
                    text-align: center;
                    width: 120px;
                    transform: translate(-50%, -50%);
                    pointer-events: none;
                ">
                    {kec.upper()}
                </div>
                """
            )
        ).add_to(m)

    return m