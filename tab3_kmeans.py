# Nama file: tab3_kmeans.py
import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import folium
from streamlit_folium import st_folium
from utils import DAFTAR_KECAMATAN, KECAMATAN_KUDUS_MAP

def render_tab3():
    st.subheader("🤖 Peta Zonasi AI (K-Means Clustering)")
    st.markdown("AI membaca **seluruh indikator (kolom)** dari semua tabel yang Anda buat secara bersamaan, lalu mengelompokkan kecamatan yang memiliki kemiripan pola masalah menjadi beberapa zona/klaster.")
    
    if not st.session_state.koleksi_tabel:
        st.warning("⚠️ Tambahkan data di Tab 1 terlebih dahulu agar AI bisa mulai belajar (Training).")
    else:
        df_master = pd.DataFrame({"Kecamatan": DAFTAR_KECAMATAN})
        fitur_tersedia = []
        
        for tabel in st.session_state.koleksi_tabel:
            df_tabel = pd.DataFrame(tabel['data'])
            for col in tabel['kolom_numerik']:
                nama_unik = f"{col} ({tabel['judul']})"
                df_master[nama_unik] = df_tabel[col]
                fitur_tersedia.append(nama_unik)
        
        if len(fitur_tersedia) < 2:
            st.info("⚠️ AI K-Means membutuhkan minimal 2 indikator (kolom) untuk bisa mengelompokkan wilayah dengan akurat. Silakan tambah kolom lagi di Tab 1.")
        else:
            col_ai1, col_ai2 = st.columns([1, 2])
            
            with col_ai1:
                st.markdown("#### ⚙️ Pengaturan AI")
                fitur_terpilih = st.multiselect("Pilih Indikator yang Dianalisis:", fitur_tersedia, default=fitur_tersedia)
                n_clusters = st.slider("Jumlah Zona Prioritas (Klaster)", min_value=2, max_value=4, value=3, help="Membagi Kudus menjadi berapa kelompok?")
                
                warna_klaster = {0: 'green', 1: 'orange', 2: 'red', 3: 'darkred'}
                label_klaster = {0: "Zona 1 (Aman/Rendah)", 1: "Zona 2 (Waspada)", 2: "Zona 3 (Kritis)", 3: "Zona 4 (Sangat Kritis)"}
                
                if st.button("🚀 Jalankan AI K-Means", type="primary") or 'Klaster_ID' not in df_master.columns:
                    if len(fitur_terpilih) >= 1:
                        X = df_master[fitur_terpilih]
                        scaler = StandardScaler()
                        X_scaled = scaler.fit_transform(X)
                        
                        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                        df_master['Klaster_ID'] = kmeans.fit_predict(X_scaled)
                        
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
                df_tampil = st.session_state.hasil_kmeans[['Kecamatan', 'Status Zona'] + fitur_terpilih]
                df_tampil = df_tampil.sort_values(by="Status Zona")
                st.dataframe(df_tampil, use_container_width=True, hide_index=True)