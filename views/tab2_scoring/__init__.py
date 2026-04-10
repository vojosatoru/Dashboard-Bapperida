# views/tab2_scoring/__init__.py
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.constants import DAFTAR_KECAMATAN

def render_tab2():
    st.subheader("🏆 Peringkat Akumulasi Prioritas Kecamatan")
    st.markdown("Skor ini dihitung **berdasarkan Kolom Acuan (yang bertombol merah)** pada masing-masing tabel di Tab 1. Kecamatan di posisi ke-1 pada suatu tabel mendapat 9 poin, ke-2 mendapat 8 poin, dst.")
    
    if not st.session_state.koleksi_tabel:
        st.info("Tambahkan minimal 1 tabel di 'Tab 1' untuk melihat perhitungan akumulasi poin.")
    else:
        # Menyiapkan kerangka data
        rekap_data = [{"Kecamatan": kec, "Total Poin": 0} for kec in DAFTAR_KECAMATAN]
        df_rekap = pd.DataFrame(rekap_data).set_index("Kecamatan")
        
        # --- PERBAIKAN: Konfigurasi Kolom untuk Mencegah Judul Terlalu Panjang ---
        config_kolom = {
            "Kecamatan": st.column_config.TextColumn("Kecamatan", width="medium"),
            "Total Poin": st.column_config.NumberColumn("Total Poin", width="small")
        }
        
        # Menghitung poin dari SETIAP TABEL (hanya berpatokan pada kolom aktif)
        for tabel in st.session_state.koleksi_tabel:
            judul, active_col, kolom_numerik = tabel['judul'], tabel['active_sort_col'], tabel['kolom_numerik']
            
            df_temp_full = pd.DataFrame(tabel['data'])
            
            # Hitung Jumlah hanya jika tabel tersebut memiliki sub-kolom numerik
            if len(kolom_numerik) > 0:
                df_temp_full['Jumlah'] = df_temp_full[kolom_numerik].sum(axis=1)
                
            df_temp = df_temp_full[['Kecamatan', active_col]]
            
            df_temp = df_temp.sort_values(by=active_col, ascending=not tabel['panah_bawah']).reset_index(drop=True)
            df_temp['Posisi'] = range(1, len(DAFTAR_KECAMATAN) + 1)
            df_temp['Poin'] = range(len(DAFTAR_KECAMATAN), 0, -1)
            
            nama_kolom_posisi = f"Pos: {judul} ({active_col})"
            
            # --- LOGIKA PENYINGKATAN JUDUL KOLOM & TOOLTIP ---
            # Jika judul lebih dari 15 huruf, potong dan tambahkan "..."
            judul_singkat = judul if len(judul) <= 15 else judul[:15] + "..."
            active_col_singkat = active_col if len(active_col) <= 15 else active_col[:15] + "..."
            label_tampil = f"Pos: {judul_singkat} ({active_col_singkat})"
            
            # Daftarkan konfigurasi ke Streamlit
            config_kolom[nama_kolom_posisi] = st.column_config.Column(
                label=label_tampil,
                help=f"Judul Tabel Asli: {judul}\nIndikator Terpilih: {active_col}", # Teks utuh muncul saat di-hover
                width="medium"
            )
            
            for _, row in df_temp.iterrows():
                df_rekap.at[row['Kecamatan'], nama_kolom_posisi] = row['Posisi']
                df_rekap.at[row['Kecamatan'], "Total Poin"] += row['Poin']
                
        df_rekap = df_rekap.reset_index().sort_values(by="Total Poin", ascending=False).reset_index(drop=True)
        kolom_posisi = [col for col in df_rekap.columns if col.startswith("Pos:")]
        
        for col in kolom_posisi:
            df_rekap[col] = df_rekap[col].fillna(0).astype(int)
            
        df_rekap = df_rekap[["Kecamatan"] + kolom_posisi + ["Total Poin"]]
        
        # 1. Tampilkan Tabel Rekapitulasi Peringkat dengan Konfigurasi Kolom
        st.dataframe(
            df_rekap.style.background_gradient(subset=["Total Poin"], cmap="Blues"), 
            use_container_width=True, 
            hide_index=True,
            column_config=config_kolom # Menyuntikkan pengaturan kolom yang baru dibuat
        )
        
        # --- FITUR BARU: VISUALISASI PIE CHART BERDASARKAN ANGKA ASLI ---
        st.markdown("---")
        st.markdown("#### 📊 Proporsi Data Indikator Asli")
        st.caption("Grafik di bawah ini menampilkan pembagian persentase berdasarkan **angka asli (raw data)** dari masing-masing kolom acuan di Tab 1, bukan berdasarkan poin peringkat.")
        
        # Membuat dataframe khusus untuk menampung angka asli
        rekap_raw_data = [{"Kecamatan": kec} for kec in DAFTAR_KECAMATAN]
        df_raw = pd.DataFrame(rekap_raw_data).set_index("Kecamatan")
        
        for tabel in st.session_state.koleksi_tabel:
            judul, active_col, kolom_numerik = tabel['judul'], tabel['active_sort_col'], tabel['kolom_numerik']
            
            df_temp_full = pd.DataFrame(tabel['data'])
            
            if len(kolom_numerik) > 0:
                df_temp_full['Jumlah'] = df_temp_full[kolom_numerik].sum(axis=1)
                
            nama_kolom_raw = f"{judul} ({active_col})"
            
            for _, row in df_temp_full.iterrows():
                df_raw.at[row['Kecamatan'], nama_kolom_raw] = row[active_col]
                
        df_raw = df_raw.reset_index()
        
        # Mengambil daftar kolom untuk dropdown (selain nama Kecamatan)
        pilihan_kolom = [col for col in df_raw.columns if col != "Kecamatan"]
        
        col_select, _ = st.columns([1, 1])
        with col_select:
            # Dropdown untuk memilih kolom mana yang mau dibuatkan Pie Chart
            if pilihan_kolom:
                kolom_terpilih = st.selectbox(
                    "Pilih indikator untuk ditampilkan pada Pie Chart:", 
                    pilihan_kolom, 
                    index=0 
                )
            else:
                kolom_terpilih = None
            
        if kolom_terpilih:
            # Pengecekan nilai negatif (Pie chart tidak bisa memproses nilai negatif)
            # Kita set nilai minimal 0 (clip) agar grafik tetap aman dirender
            df_plot = df_raw[['Kecamatan', kolom_terpilih]].copy()
            df_plot[kolom_terpilih] = df_plot[kolom_terpilih].clip(lower=0)

            # Membuat grafik Pie Chart menggunakan Plotly Express
            fig = px.pie(
                df_plot, 
                values=kolom_terpilih, 
                names='Kecamatan', 
                title=f"Distribusi Angka Asli: <b>{kolom_terpilih}</b>",
                color_discrete_sequence=px.colors.qualitative.Pastel 
            )
            
            # Merapikan tampilan (menambahkan persentase di dalam kue, label angka asli saat di-hover)
            fig.update_traces(
                textposition='inside', 
                textinfo='percent+label', 
                hovertemplate="<b>%{label}</b><br>Angka Asli: %{value}<br>Proporsi: %{percent}"
            )
            
            # Menghapus background agar menyatu dengan mode Gelap/Terang Streamlit
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            
            # Menampilkan grafik ke layar
            st.plotly_chart(fig, use_container_width=True)