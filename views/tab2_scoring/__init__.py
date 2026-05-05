# views/tab2_scoring/__init__.py
import streamlit as st
import pandas as pd
import plotly.express as px
import io
from utils.constants import DAFTAR_KECAMATAN

def konversi_df_ke_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Peringkat')
    processed_data = output.getvalue()
    return processed_data

def render_tab2():
    st.subheader("🏆 Peringkat Akumulasi Prioritas Kecamatan")
    st.markdown("Skor ini dihitung **berdasarkan Kolom Acuan (yang bertombol merah)** pada masing-masing tabel di Tab 1.")
    
    # --- FITUR BARU: Menyaring Hanya Tabel yang Aktif ---
    tabel_aktif = [t for t in st.session_state.koleksi_tabel if t.get('is_active', True)]
    
    if not tabel_aktif:
        if not st.session_state.koleksi_tabel:
            st.info("Tambahkan minimal 1 tabel di 'Tab 1' untuk melihat perhitungan akumulasi poin.")
        else:
            st.info("Semua tabel saat ini berstatus 'Mati/Nonaktif'. Silakan aktifkan minimal 1 tabel di Tab 1 untuk memunculkan peringkat.")
    else:
        rekap_data = [{"Kecamatan": kec, "Total Poin": 0} for kec in DAFTAR_KECAMATAN]
        df_rekap = pd.DataFrame(rekap_data).set_index("Kecamatan")
        
        config_kolom = {
            "Kecamatan": st.column_config.TextColumn("Kecamatan", width="medium"),
            "Total Poin": st.column_config.NumberColumn("Total Poin", width="small")
        }
        
        for tabel in tabel_aktif:
            judul, active_col, kolom_numerik = tabel['judul'], tabel['active_sort_col'], tabel['kolom_numerik']
            df_temp_full = pd.DataFrame(tabel['data'])
            
            if len(kolom_numerik) > 0:
                df_temp_full['Jumlah'] = df_temp_full[kolom_numerik].sum(axis=1)
                
            df_temp = df_temp_full[['Kecamatan', active_col]]
            df_temp = df_temp.sort_values(by=active_col, ascending=not tabel['panah_bawah']).reset_index(drop=True)
            df_temp['Posisi'] = range(1, len(DAFTAR_KECAMATAN) + 1)
            df_temp['Poin'] = range(len(DAFTAR_KECAMATAN), 0, -1)
            
            nama_kolom_posisi = f"Pos: {judul} ({active_col})"
            judul_singkat = judul if len(judul) <= 15 else judul[:15] + "..."
            active_col_singkat = active_col if len(active_col) <= 15 else active_col[:15] + "..."
            label_tampil = f"Pos: {judul_singkat} ({active_col_singkat})"
            
            config_kolom[nama_kolom_posisi] = st.column_config.Column(
                label=label_tampil, help=f"Judul Tabel Asli: {judul}\nIndikator Terpilih: {active_col}", width="medium"
            )
            
            for _, row in df_temp.iterrows():
                df_rekap.at[row['Kecamatan'], nama_kolom_posisi] = row['Posisi']
                df_rekap.at[row['Kecamatan'], "Total Poin"] += row['Poin']
                
        df_rekap = df_rekap.reset_index().sort_values(by="Total Poin", ascending=False).reset_index(drop=True)
        kolom_posisi = [col for col in df_rekap.columns if col.startswith("Pos:")]
        for col in kolom_posisi:
            df_rekap[col] = df_rekap[col].fillna(0).astype(int)
            
        df_rekap = df_rekap[["Kecamatan"] + kolom_posisi + ["Total Poin"]]
        
        try:
            st.dataframe(df_rekap.style.background_gradient(subset=["Total Poin"], cmap="Blues").format(thousands="."), use_container_width=True, hide_index=True, column_config=config_kolom)
        except NameError:
            st.dataframe(df_rekap.style.background_gradient(subset=["Total Poin"], cmap="Blues").format(thousands="."), use_container_width=True, hide_index=True)
            
        excel_data = konversi_df_ke_excel(df_rekap)
        st.download_button(label="📥 Unduh Tabel Peringkat", data=excel_data, file_name='Rekap_Peringkat.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', type="primary")
        
        st.markdown("---")
        st.markdown("#### 📊 Proporsi Data Indikator Asli")
        st.caption("💡 **Tip:** Arahkan mouse ke atas grafik, lalu klik ikon Kamera untuk mengunduh Pie Chart.")
        
        rekap_raw_data = [{"Kecamatan": kec} for kec in DAFTAR_KECAMATAN]
        df_raw = pd.DataFrame(rekap_raw_data).set_index("Kecamatan")
        
        for tabel in tabel_aktif:
            judul, active_col, kolom_numerik = tabel['judul'], tabel['active_sort_col'], tabel['kolom_numerik']
            df_temp_full = pd.DataFrame(tabel['data'])
            if len(kolom_numerik) > 0:
                df_temp_full['Jumlah'] = df_temp_full[kolom_numerik].sum(axis=1)
            nama_kolom_raw = f"{judul} ({active_col})"
            for _, row in df_temp_full.iterrows():
                df_raw.at[row['Kecamatan'], nama_kolom_raw] = row[active_col]
                
        df_raw = df_raw.reset_index()
        pilihan_kolom = [col for col in df_raw.columns if col != "Kecamatan"]
        
        col_select, _ = st.columns([1, 1])
        with col_select:
            if pilihan_kolom:
                kolom_terpilih = st.selectbox("Pilih indikator untuk ditampilkan pada Pie Chart:", pilihan_kolom, index=0)
            else:
                kolom_terpilih = None
            
        if kolom_terpilih:
            df_plot = df_raw[['Kecamatan', kolom_terpilih]].copy()
            df_plot[kolom_terpilih] = df_plot[kolom_terpilih].clip(lower=0)

            fig = px.pie(df_plot, values=kolom_terpilih, names='Kecamatan', title=f"Distribusi Angka Asli: <b>{kolom_terpilih}</b>", color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_traces(textposition='inside', textinfo='percent+label', hovertemplate="<b>%{label}</b><br>Angka Asli: %{value}<br>Proporsi: %{percent}")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})