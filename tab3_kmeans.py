# Nama file: tab3_kmeans.py
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import folium
from streamlit_folium import st_folium
from utils import DAFTAR_KECAMATAN, KECAMATAN_KUDUS_MAP
import os
import json

# File untuk menyimpan konfigurasi Tab 3 agar kebal dari Refresh (F5)
CONFIG_FILE_KMEANS = "config_kmeans.json"

def muat_config_kmeans():
    if os.path.exists(CONFIG_FILE_KMEANS):
        try:
            with open(CONFIG_FILE_KMEANS, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def simpan_config_kmeans(data):
    with open(CONFIG_FILE_KMEANS, "w") as f:
        json.dump(data, f)

def render_tab3():
    st.subheader("🤖 Peta Zonasi AI (K-Means Clustering)")
    st.markdown("AI membaca indikator yang dipilih dan **menyelaraskan nilainya secara otomatis** (berdasarkan arah panah ⬇️/⬆️ di Tab 1), lalu mengelompokkan kecamatan ke dalam zona prioritas (Natural Breaks/Multi-dimensional Clustering).")
    
    if not st.session_state.koleksi_tabel:
        st.warning("⚠️ Tambahkan data di Tab 1 terlebih dahulu agar AI bisa mulai belajar (Training).")
    else:
        df_master = pd.DataFrame({"Kecamatan": DAFTAR_KECAMATAN})
        df_untuk_ai = pd.DataFrame({"Kecamatan": DAFTAR_KECAMATAN}) # Data yang sudah di-invers khusus untuk mesin AI
        fitur_tersedia = []
        
        for tabel in st.session_state.koleksi_tabel:
            df_tabel = pd.DataFrame(tabel['data'])
            arah_panah_bawah = tabel['panah_bawah'] # Membaca status kriteria (Cost/Benefit)
            
            # Menambahkan kolom 'Jumlah' untuk semua jenis tabel
            if len(tabel['kolom_numerik']) > 0:
                # Hitung ulang kolom Jumlah agar bisa dipilih
                df_tabel['Jumlah'] = df_tabel[tabel['kolom_numerik']].sum(axis=1)
                kolom_analisis = tabel['kolom_numerik'] + ["Jumlah"]
            else:
                kolom_analisis = ["Jumlah"]
            
            for col in kolom_analisis:
                nama_unik = f"{col} ({tabel['judul']})"
                
                # Data asli untuk ditampilkan ke user
                df_master[nama_unik] = df_tabel[col]
                
                # --- LOGIKA INVERS UNTUK AI ---
                if arah_panah_bawah:
                    # Kriteria Cost (Nilai tinggi = Parah). Tidak perlu diubah.
                    df_untuk_ai[nama_unik] = df_tabel[col]
                else:
                    # Kriteria Benefit (Nilai rendah = Parah). 
                    # DI-INVERS: Dikalikan -1 agar AI paham bahwa nilai yang makin kecil ini justru makin bermasalah
                    df_untuk_ai[nama_unik] = df_tabel[col] * -1 
                    
                fitur_tersedia.append(nama_unik)
        
        if len(fitur_tersedia) < 1:
            st.info("⚠️ AI K-Means membutuhkan minimal 1 indikator (kolom) untuk bisa mengelompokkan wilayah. Silakan tambah data di Tab 1.")
        else:
            col_ai1, col_ai2 = st.columns([1, 2])
            
            with col_ai1:
                st.markdown("#### ⚙️ Pengaturan AI")
                
                # --- PERBAIKAN TOTAL: Membaca & Menyimpan Konfigurasi ke File JSON ---
                config_ai = muat_config_kmeans()
                
                # Ambil histori pilihan dari file, jika kosong gunakan semua fitur
                saved_features = config_ai.get('ai_selected_features', fitur_tersedia)
                
                # Saring histori (membuang fitur yang mungkin sudah dihapus pengguna dari Tab 1)
                valid_features = [f for f in saved_features if f in fitur_tersedia]
                
                # Jika setelah disaring kosong, kembali gunakan semua fitur
                if not valid_features and fitur_tersedia:
                    valid_features = fitur_tersedia

                fitur_terpilih = st.multiselect(
                    "Pilih Indikator yang Dianalisis:", 
                    fitur_tersedia, 
                    default=valid_features
                )
                
                # Simpan otomatis ke file JSON jika ada perubahan pilihan
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
                
                # Simpan otomatis nilai klaster ke file JSON
                if n_clusters != config_ai.get('ai_n_clusters'):
                    config_ai['ai_n_clusters'] = n_clusters
                    simpan_config_kmeans(config_ai)
                
                warna_klaster = {0: 'green', 1: 'orange', 2: 'red', 3: 'darkred'}
                label_klaster = {0: "Zona 1 (Aman/Rendah)", 1: "Zona 2 (Waspada)", 2: "Zona 3 (Kritis)", 3: "Zona 4 (Sangat Kritis)"}
                
                if st.button("🚀 Jalankan AI K-Means", type="primary") or 'Klaster_ID' not in df_master.columns:
                    if len(fitur_terpilih) >= 1:
                        # 1. Mengambil data yang sudah diselaraskan (termasuk yang di-invers)
                        X = df_untuk_ai[fitur_terpilih]
                        
                        # 2. Scaling Data
                        scaler = StandardScaler()
                        X_scaled = scaler.fit_transform(X)
                        
                        # 3. Proses K-Means
                        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                        klaster_mentah = kmeans.fit_predict(X_scaled)
                        
                        # --- LOGIKA SORTING CENTROID (PENTING) ---
                        # Agar Klaster 0 selalu Aman (Hijau) dan Klaster tertinggi selalu Kritis (Merah)
                        rata_rata_klaster = []
                        for i in range(n_clusters):
                            # Menghitung rata-rata nilai tiap klaster
                            rata_rata_klaster.append(X_scaled[klaster_mentah == i].mean())
                        
                        # Membuat pemetaan urutan klaster dari rata-rata terkecil hingga terbesar
                        urutan_baru = {old_id: new_id for new_id, old_id in enumerate(np.argsort(rata_rata_klaster))}
                        
                        # Terapkan ID klaster yang sudah diurutkan ke data master
                        df_master['Klaster_ID'] = [urutan_baru[k] for k in klaster_mentah]
                        
                        df_master['Status Zona'] = df_master['Klaster_ID'].map(label_klaster)
                        df_master['Koordinat'] = df_master['Kecamatan'].map(KECAMATAN_KUDUS_MAP)
                        st.session_state.hasil_kmeans = df_master
            
            with col_ai2:
                if 'hasil_kmeans' in st.session_state:
                    df_hasil = st.session_state.hasil_kmeans
                    st.markdown("#### 🗺️ Peta Prioritas Wilayah")
                    
                    peta_kudus = folium.Map(location=[-6.8048, 110.8405], zoom_start=11)
                    for idx, row in df_hasil.iterrows():
                        koordinat = row['Koordinat']
                        klaster_id = row['Klaster_ID']
                        
                        # Tooltip menampilkan data ASLI, bukan data invers
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
                st.dataframe(df_tampil, use_container_width=True, hide_index=True)