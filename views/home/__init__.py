# views/home/__init__.py
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.constants import DAFTAR_KECAMATAN

def render_home():
    st.subheader("🏠 Beranda Executive Bapperida")
    st.markdown("Selamat datang di **Sistem Pendukung Keputusan & AI Spasial Kabupaten Kudus**. Berikut adalah ringkasan (*Executive Summary*) dari data yang telah dianalisis.")
    st.markdown("---")
    
    ada_data = len(st.session_state.koleksi_tabel) > 0
    if not ada_data:
        st.info("👋 Selamat Datang! Saat ini belum ada data indikator yang dimasukkan. Silakan menuju menu **Input Data Indikator** untuk memulai.")
        return

    # --- FITUR BARU: Menyaring Hanya Tabel yang Aktif ---
    tabel_aktif = [t for t in st.session_state.koleksi_tabel if t.get('is_active', True)]
    
    if not tabel_aktif:
        st.info("👋 Saat ini seluruh tabel indikator sedang dinonaktifkan. Silakan nyalakan minimal 1 tabel di **Input Data Indikator** untuk melihat Ringkasan Executive.")
        return

    # 1. Total Indikator
    total_tabel = len(tabel_aktif)
    total_indikator = sum([len(t['kolom_numerik']) if len(t['kolom_numerik']) > 0 else 1 for t in tabel_aktif])
    
    # 2. Menghitung Peringkat Prioritas Cepat
    rekap_data = [{"Kecamatan": kec, "Total Poin": 0} for kec in DAFTAR_KECAMATAN]
    df_rekap = pd.DataFrame(rekap_data).set_index("Kecamatan")
    
    for tabel in tabel_aktif:
        active_col = tabel['active_sort_col']
        df_temp_full = pd.DataFrame(tabel['data'])
        
        for col in df_temp_full.columns:
            if col != "Kecamatan":
                df_temp_full[col] = pd.to_numeric(df_temp_full[col], errors='coerce').fillna(0)
        
        if len(tabel['kolom_numerik']) > 0:
            df_temp_full['Jumlah'] = df_temp_full[tabel['kolom_numerik']].sum(axis=1)
            
        df_temp = df_temp_full[['Kecamatan', active_col]]
        df_temp = df_temp.sort_values(by=active_col, ascending=not tabel['panah_bawah']).reset_index(drop=True)
        df_temp['Poin'] = range(len(DAFTAR_KECAMATAN), 0, -1)
        for _, row in df_temp.iterrows():
            df_rekap.at[row['Kecamatan'], "Total Poin"] += row['Poin']
            
    df_rekap = df_rekap.reset_index().sort_values(by="Total Poin", ascending=False)
    
    poin_tertinggi = df_rekap['Total Poin'].max()
    kecamatan_tertinggi = df_rekap[df_rekap['Total Poin'] == poin_tertinggi]['Kecamatan'].tolist()
    kec_prioritas = ", ".join(kecamatan_tertinggi)
    
    # 3. Status AI K-Means
    status_ai = "Belum Dijalankan"
    if 'hasil_kmeans' in st.session_state and 'Klaster_ID' in st.session_state.hasil_kmeans.columns:
        df_kmeans = st.session_state.hasil_kmeans
        klaster_terparah_id = df_kmeans['Klaster_ID'].max()
        zona_terparah = df_kmeans[df_kmeans['Klaster_ID'] == klaster_terparah_id]
        jumlah_terparah = len(zona_terparah)
        nama_zona_terparah = zona_terparah.iloc[0]['Status Zona']
        status_ai = f"{jumlah_terparah} Kec. di {nama_zona_terparah}"

    # --- MENAMPILKAN KARTU METRIK ---
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.metric(label="📊 Total Indikator Dianalisis", value=f"{total_indikator} Indikator", delta=f"Dari {total_tabel} Tabel Aktif", delta_color="normal")
    with col2:
        with st.container(border=True):
            st.metric(label="🚨 Prioritas Pembangunan Utama", value=kec_prioritas, delta=f"Skor Akumulasi: {poin_tertinggi}", delta_color="inverse")
    with col3:
        with st.container(border=True):
            d_color = "off" if status_ai == "Belum Dijalankan" else "normal"
            st.metric(label="🤖 Status Peta AI Zonasi", value=status_ai, delta="Cek Tab Peta Zonasi" if status_ai != "Belum Dijalankan" else "Menunggu Proses", delta_color=d_color)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- MENAMPILKAN GRAFIK RINGKASAN ---
    col_chart1, col_chart2 = st.columns([2, 1])
    with col_chart1:
        st.markdown("#### 📈 Peringkat Akumulasi Tertinggi (Top 5)")
        df_top5 = df_rekap.head(5).sort_values(by="Total Poin", ascending=True) 
        fig_bar = px.bar(
            df_top5, x="Total Poin", y="Kecamatan", orientation='h', text="Total Poin", color="Total Poin", color_continuous_scale="Reds"
        )
        fig_bar.update_traces(textposition='inside')
        fig_bar.update_layout(xaxis_title="Total Poin Scoring", yaxis_title="", coloraxis_showscale=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=0, b=0), height=300)
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col_chart2:
        st.markdown("#### 💡 Insight Cepat")
        st.info(f"Kecamatan **{kec_prioritas}** memimpin sebagai wilayah prioritas berdasarkan gabungan dari **{total_indikator} indikator** aktif.")
        if status_ai != "Belum Dijalankan":
            st.warning(f"Sistem AI mendeteksi ada **{status_ai}** berdasarkan pola multi-dimensi saat ini.")
        else:
            st.success("Silakan menuju menu **AI Peta Zonasi** untuk membiarkan mesin mengelompokkan wilayah secara otomatis.")