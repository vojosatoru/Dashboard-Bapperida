# views/tab3_kmeans/__init__.py
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import folium
from streamlit_folium import st_folium
import os
import json

from utils.constants import DAFTAR_KECAMATAN, KECAMATAN_KUDUS_MAP
from utils.state_manager import muat_config_kmeans, simpan_config_kmeans

def render_tab3():
    st.subheader("🤖 Peta Zonasi AI (K-Means Clustering)")
    st.markdown("AI membaca indikator yang dipilih dan **menyelaraskan nilainya secara otomatis** (berdasarkan arah pengurutan Terbesar/Terkecil di Tab 1), lalu mengelompokkan kecamatan ke dalam zona prioritas (Natural Breaks/Multi-dimensional Clustering).")
    
    if not st.session_state.koleksi_tabel:
        st.warning("⚠️ Tambahkan data di Tab 1 terlebih dahulu agar AI bisa mulai belajar (Training).")
    else:
        df_master = pd.DataFrame({"Kecamatan": DAFTAR_KECAMATAN})
        df_untuk_ai = pd.DataFrame({"Kecamatan": DAFTAR_KECAMATAN}) 
        fitur_tersedia = []
        
        for tabel in st.session_state.koleksi_tabel:
            df_tabel = pd.DataFrame(tabel['data'])
            arah_panah_bawah = tabel['panah_bawah'] 
            
            if len(tabel['kolom_numerik']) > 0:
                df_tabel['Jumlah'] = df_tabel[tabel['kolom_numerik']].sum(axis=1)
                kolom_analisis = tabel['kolom_numerik'] + ["Jumlah"]
            else:
                kolom_analisis = ["Jumlah"]
            
            for col in kolom_analisis:
                nama_unik = f"{col} ({tabel['judul']})"
                df_master[nama_unik] = df_tabel[col]
                
                if arah_panah_bawah:
                    df_untuk_ai[nama_unik] = df_tabel[col]
                else:
                    df_untuk_ai[nama_unik] = df_tabel[col] * -1 
                    
                fitur_tersedia.append(nama_unik)
        
        if len(fitur_tersedia) < 1:
            st.info("⚠️ AI K-Means membutuhkan minimal 1 indikator (kolom) untuk bisa mengelompokkan wilayah.")
        else:
            col_ai1, col_ai2 = st.columns([1, 2])
            
            # Mendefinisikan warna agar bisa diakses oleh kedua kolom (Peta dan Pengaturan AI)
            warna_klaster_hex = {0: '#28a745', 1: '#fd7e14', 2: '#dc3545', 3: '#8b0000'}
            warna_klaster = {0: 'green', 1: 'orange', 2: 'red', 3: 'darkred'}
            label_klaster = {0: "Zona 1 (Aman/Rendah)", 1: "Zona 2 (Waspada)", 2: "Zona 3 (Kritis)", 3: "Zona 4 (Sangat Kritis)"}

            with col_ai1:
                st.markdown("#### ⚙️ Pengaturan AI")
                
                config_ai = muat_config_kmeans()
                saved_features = config_ai.get('ai_selected_features', fitur_tersedia)
                valid_features = [f for f in saved_features if f in fitur_tersedia]
                
                if not valid_features and fitur_tersedia:
                    valid_features = fitur_tersedia

                fitur_terpilih = st.multiselect(
                    "Pilih Indikator yang Dianalisis:", 
                    fitur_tersedia, 
                    default=valid_features
                )
                
                if fitur_terpilih != config_ai.get('ai_selected_features'):
                    config_ai['ai_selected_features'] = fitur_terpilih
                    simpan_config_kmeans(config_ai)
                
                saved_cluster = config_ai.get('ai_n_clusters', 3)
                n_clusters = st.slider(
                    "Jumlah Zona Prioritas (Klaster)", 
                    min_value=2, max_value=4, 
                    value=saved_cluster, 
                    help="Membagi Kudus menjadi berapa kelompok?"
                )
                
                if n_clusters != config_ai.get('ai_n_clusters'):
                    config_ai['ai_n_clusters'] = n_clusters
                    simpan_config_kmeans(config_ai)
                
                if st.button("🚀 Jalankan AI K-Means", type="primary") or 'Klaster_ID' not in df_master.columns:
                    if len(fitur_terpilih) >= 1:
                        X = df_untuk_ai[fitur_terpilih]
                        scaler = StandardScaler()
                        X_scaled = scaler.fit_transform(X)
                        
                        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                        klaster_mentah = kmeans.fit_predict(X_scaled)
                        
                        rata_rata_klaster = []
                        for i in range(n_clusters):
                            rata_rata_klaster.append(X_scaled[klaster_mentah == i].mean())
                        
                        urutan_baru = {old_id: new_id for new_id, old_id in enumerate(np.argsort(rata_rata_klaster))}
                        
                        df_master['Klaster_ID'] = [urutan_baru[k] for k in klaster_mentah]
                        df_master['Status Zona'] = df_master['Klaster_ID'].map(label_klaster)
                        df_master['Koordinat'] = df_master['Kecamatan'].map(KECAMATAN_KUDUS_MAP)
                        st.session_state.hasil_kmeans = df_master
            
            with col_ai2:
                if 'hasil_kmeans' in st.session_state:
                    df_hasil = st.session_state.hasil_kmeans
                    
                    st.markdown("#### 🗺️ Peta Prioritas Wilayah")
                    
                    # --- FITUR TOMBOL PENGGANTI MODE PETA ---
                    mode_pilihan = st.radio("Mode Tampilan Peta:", ["Arsir (Poligon)", "Pin (Marker)"], horizontal=True)
                    
                    geojson_path = "data/kudus_kecamatan.geojson"
                    mode_arsiran = (mode_pilihan == "Arsir (Poligon)") and os.path.exists(geojson_path)

                    # Inisialisasi Peta
                    peta_kudus = folium.Map(location=[-6.8048, 110.8405], zoom_start=11)
                    
                    if mode_arsiran:
                        # MENGGUNAKAN MODE ARSIRAN (POLIGON)
                        try:
                            with open(geojson_path, "r", encoding="utf-8") as f:
                                kudus_geo = json.load(f)
                            
                            # Auto-Detector: Mencari key (kunci) yang menyimpan nama kecamatan
                            kec_key = None
                            for feature in kudus_geo['features']:
                                for k, v in feature['properties'].items():
                                    if isinstance(v, str) and v.title() in DAFTAR_KECAMATAN:
                                        kec_key = k
                                        break
                                if kec_key: break
                            
                            if not kec_key:
                                st.error("❌ File GeoJSON tidak valid atau tidak memiliki daftar nama Kecamatan di Kudus.")
                            else:
                                lookup_data = df_hasil.set_index('Kecamatan').to_dict('index')
                                
                                for feature in kudus_geo['features']:
                                    kec_name = feature['properties'].get(kec_key, "").title()
                                    if kec_name in lookup_data:
                                        feature['properties']['Status_Zona_Visual'] = lookup_data[kec_name]['Status Zona']
                                        for f_name in fitur_terpilih:
                                            aman_f_name = f_name.replace(".", "_")
                                            feature['properties'][aman_f_name] = str(lookup_data[kec_name][f_name])
                                            
                                tooltip_fields = [kec_key, 'Status_Zona_Visual'] + [f.replace(".", "_") for f in fitur_terpilih]
                                tooltip_aliases = ['Kecamatan:', 'Zona:'] + [f"{f}:" for f in fitur_terpilih]
                                
                                folium.GeoJson(
                                    kudus_geo,
                                    style_function=lambda feature: {
                                        'fillColor': warna_klaster_hex.get(
                                            lookup_data.get(feature['properties'].get(kec_key, "").title(), {}).get('Klaster_ID', -1),
                                            '#cccccc' # Warna abu-abu jika kecamatan tidak ditemukan
                                        ),
                                        'color': 'black',     # Warna garis batas
                                        'weight': 1.5,        # Ketebalan garis batas
                                        'fillOpacity': 0.7,   # Transparansi arsiran
                                    },
                                    tooltip=folium.GeoJsonTooltip(
                                        fields=tooltip_fields,
                                        aliases=tooltip_aliases,
                                        style="background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;"
                                    )
                                ).add_to(peta_kudus)
                                
                        except Exception as e:
                            st.error(f"Terjadi kesalahan saat memproses GeoJSON: {e}")
                    
                    else:
                        # MENGGUNAKAN MODE PIN (MARKER)
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
                    
                    st_folium(peta_kudus, width=700, height=450)
            
            st.markdown("#### 📊 Tabel Rincian Anggota Klaster")
            if 'hasil_kmeans' in st.session_state:
                # Tampilkan tabel asli, tapi sudah diurutkan berdasarkan zona
                df_tampil = st.session_state.hasil_kmeans[['Kecamatan', 'Status Zona'] + fitur_terpilih]
                df_tampil = df_tampil.sort_values(by="Status Zona")
                
                # --- PERBAIKAN: Konfigurasi Kolom untuk Mencegah Judul Terlalu Panjang di Tab 3 ---
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
                    df_tampil, 
                    use_container_width=True, 
                    hide_index=True,
                    column_config=config_kolom_tab3
                )