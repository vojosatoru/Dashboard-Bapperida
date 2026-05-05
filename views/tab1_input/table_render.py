# views/tab1_input/table_render.py
import streamlit as st
import pandas as pd
import copy
import random
from utils.constants import DAFTAR_KECAMATAN
from utils.state_manager import init_history, simpan_data
from utils.styling import beri_warna_tabel
from views.tab1_input.form_add_col import render_step_3

from views.tab1_input.backup_ui import render_backup_ui

def render_tables():
    render_backup_ui()

    st.markdown("---")
    
    if not st.session_state.koleksi_tabel:
        st.info("Belum ada data yang ditambahkan. Klik '+ Tambah Data Baru' atau 'Auto Import' untuk memulai.")
    else:
        st.caption("💡 Tip: Gunakan menu di bawah judul tabel untuk mengelola data dengan rapi.")
        for i, tabel in enumerate(st.session_state.koleksi_tabel):
            init_history(st.session_state.koleksi_tabel[i])
            tabel = st.session_state.koleksi_tabel[i]
            
            tabel_id = tabel['id']
            kolom_numerik = tabel['kolom_numerik']
            hapus_jumlah = tabel.get('hapus_jumlah', False) 
            
            is_form_open = st.session_state.form_step == 3
            
            # --- FITUR BARU: Deteksi Status Aktif ---
            is_active = tabel.get('is_active', True)
            
            # --- DERETAN TOMBOL KONTROL TABEL ---
            # Proporsi kolom disesuaikan untuk memberi ruang bagi Toggle
            top_col1, top_col_tog, top_col2, top_col_undo, top_col_redo, top_col_add, top_col3 = st.columns([2.9, 1.1, 0.4, 1, 1, 1, 1])
            
            if is_active:
                top_col1.markdown(f"### {tabel['judul']}")
            else:
                top_col1.markdown(f"### <span style='color:#777777;'><s>{tabel['judul']}</s> (Mati)</span>", unsafe_allow_html=True)
            
            # --- SAKELAR ON/OFF ---
            new_is_active = top_col_tog.toggle(
                "🟢 Aktif" if is_active else "⚫ Mati", 
                value=is_active, 
                key=f"tog_{tabel_id}", 
                help="Matikan untuk mengecualikan tabel ini dari perhitungan AI dan Peringkat tanpa menghapusnya."
            )
            
            if new_is_active != is_active:
                st.session_state.koleksi_tabel[i]['is_active'] = new_is_active
                simpan_data(st.session_state.koleksi_tabel) 
                st.session_state.pop('hasil_kmeans', None) # Sinkronkan AI
                st.rerun()

            warna_baru = top_col2.color_picker("Warna", value=tabel['warna'], key=f"btn_warna_{tabel_id}", label_visibility="collapsed", disabled=(is_form_open or not is_active))
            if warna_baru != tabel['warna']:
                st.session_state.koleksi_tabel[i]['warna'] = warna_baru
                simpan_data(st.session_state.koleksi_tabel) 
                st.rerun()

            can_undo = (tabel['history_index'] > 0) and not is_form_open and is_active
            can_redo = (tabel['history_index'] < len(tabel['history']) - 1) and not is_form_open and is_active
            
            if top_col_undo.button("↩️ Undo", key=f"undo_{tabel_id}", disabled=not can_undo, help="Mundurkan riwayat kolom", use_container_width=True):
                tabel['history_index'] -= 1
                state = tabel['history'][tabel['history_index']]
                tabel['data'] = copy.deepcopy(state['data'])
                tabel['kolom_numerik'] = copy.deepcopy(state['kolom_numerik'])
                tabel['hapus_jumlah'] = state['hapus_jumlah']
                tabel['active_sort_col'] = state['active_sort_col']
                simpan_data(st.session_state.koleksi_tabel)
                st.session_state.pop('hasil_kmeans', None)
                st.rerun()

            if top_col_redo.button("↪️ Redo", key=f"redo_{tabel_id}", disabled=not can_redo, help="Majukan riwayat kolom", use_container_width=True):
                tabel['history_index'] += 1
                state = tabel['history'][tabel['history_index']]
                tabel['data'] = copy.deepcopy(state['data'])
                tabel['kolom_numerik'] = copy.deepcopy(state['kolom_numerik'])
                tabel['hapus_jumlah'] = state['hapus_jumlah']
                tabel['active_sort_col'] = state['active_sort_col']
                simpan_data(st.session_state.koleksi_tabel)
                st.session_state.pop('hasil_kmeans', None)
                st.rerun()
                
            if top_col_add.button("➕ Kolom", key=f"add_col_{tabel_id}", help="Tambah indikator baru", use_container_width=True, disabled=(is_form_open or not is_active)):
                st.session_state.form_step = 3
                st.session_state.edit_table_id = tabel_id
                st.session_state.angka_acak_kolom_baru = {kec: random.randint(10, 999) for kec in DAFTAR_KECAMATAN}
                st.session_state.angka_acak_kolom_baru_2 = {kec: random.randint(10, 999) for kec in DAFTAR_KECAMATAN}
                st.rerun()
                
            if top_col3.button("❌ Hapus", key=f"btn_hapus_tabel_{tabel_id}", help="Hapus Tabel Total", disabled=is_form_open, use_container_width=True):
                st.session_state.koleksi_tabel.pop(i)
                simpan_data(st.session_state.koleksi_tabel) 
                st.session_state.pop('hasil_kmeans', None)
                st.rerun()

            if st.session_state.form_step == 3 and st.session_state.get('edit_table_id') == tabel_id:
                render_step_3(tabel_id, tabel)

            kolom_tampil = []
            if len(kolom_numerik) > 0:
                kolom_tampil.extend(kolom_numerik)
                if not hapus_jumlah:
                    kolom_tampil.append("Jumlah")
            else:
                if not hapus_jumlah:
                    kolom_tampil.append("Jumlah")

            if not kolom_tampil:
                st.info("Semua kolom telah dihapus. Menghapus tabel secara otomatis...")
                st.session_state.koleksi_tabel.pop(i)
                simpan_data(st.session_state.koleksi_tabel)
                st.session_state.pop('hasil_kmeans', None)
                st.rerun()
                continue 

            # --- BARIS PERTAMA PENGATURAN ---
            row1_col1, row1_col2 = st.columns(2)
            
            with row1_col1:
                with st.expander("✏️ Ubah Nama Tabel", expanded=False):
                    st.markdown("**Ganti Nama:**")
                    col_rn_input, col_rn_btn = st.columns([3, 1])
                    judul_baru = col_rn_input.text_input("Nama Baru", value=tabel['judul'], key=f"rename_exp_{tabel_id}", label_visibility="collapsed", disabled=not is_active)
                    
                    if col_rn_btn.button("Simpan", key=f"btn_save_name_{tabel_id}", use_container_width=True, type="primary", disabled=not is_active):
                        if judul_baru.strip() and judul_baru.strip() != tabel['judul']:
                            st.session_state.koleksi_tabel[i]['judul'] = judul_baru.strip()
                            simpan_data(st.session_state.koleksi_tabel)
                            st.rerun()
                            
            with row1_col2:
                with st.expander("📌 Pengaturan Urutan", expanded=False):
                    st.markdown("**Urutkan Peringkat Berdasarkan:**")
                    col_sort, col_dir = st.columns([2, 1])
                    
                    sort_idx = kolom_tampil.index(tabel['active_sort_col']) if tabel['active_sort_col'] in kolom_tampil else 0
                    sort_choice = col_sort.selectbox("Pilih Kolom:", kolom_tampil, index=sort_idx, key=f"sort_sel_{tabel_id}", label_visibility="collapsed", disabled=not is_active)
                    
                    dir_choice = col_dir.selectbox("Arah:", ["⬇️ Terbesar", "⬆️ Terkecil"], index=0 if tabel['panah_bawah'] else 1, key=f"dir_sel_{tabel_id}", label_visibility="collapsed", disabled=not is_active)
                    is_panah_bawah = (dir_choice == "⬇️ Terbesar")
                    
                    if sort_choice != tabel['active_sort_col'] or is_panah_bawah != tabel['panah_bawah']:
                        st.session_state.koleksi_tabel[i]['active_sort_col'] = sort_choice
                        st.session_state.koleksi_tabel[i]['panah_bawah'] = is_panah_bawah
                        simpan_data(st.session_state.koleksi_tabel)
                        st.session_state.pop('hasil_kmeans', None)
                        st.rerun()

            # --- BARIS KEDUA PENGATURAN ---
            row2_col1, row2_col2 = st.columns(2)
            
            with row2_col1:
                with st.expander("⚖️ Sesuaikan Proporsi / Rasio", expanded=False):
                    st.markdown("**Bagi angka mentah menjadi perbandingan yang adil:**")
                    
                    pilihan_norm = ["Absolut", "Dibagi Penduduk", "Dibagi Luas Area", "Dibagi Keduanya"]
                    norm_aktif = tabel.get('normalisasi', 'Absolut')
                    
                    if norm_aktif == "Per Kapita (Bagi Penduduk)": norm_aktif = "Dibagi Penduduk"
                    elif norm_aktif == "Kepadatan (Bagi Luas Area)": norm_aktif = "Dibagi Luas Area"
                    elif norm_aktif == "Rasio Ganda (Bagi Penduduk & Luas Area)": norm_aktif = "Dibagi Keduanya"
                        
                    idx_norm = pilihan_norm.index(norm_aktif) if norm_aktif in pilihan_norm else 0
                    
                    norm_baru = st.selectbox(
                        "Pilih Metode:", pilihan_norm, index=idx_norm, key=f"norm_sel_{tabel_id}", label_visibility="collapsed", disabled=not is_active
                    )
                    
                    if norm_baru != tabel.get('normalisasi', 'Absolut'):
                        st.session_state.koleksi_tabel[i]['normalisasi'] = norm_baru
                        simpan_data(st.session_state.koleksi_tabel)
                        st.session_state.pop('hasil_kmeans', None)
                        st.rerun()

            with row2_col2:
                with st.expander("🗑️ Hapus Kolom", expanded=False):
                    st.markdown("**Hapus Indikator/Kolom:**")
                    col_del_sel, col_del_btn = st.columns([2, 1])
                    del_choice = col_del_sel.selectbox("Pilih Kolom:", ["-- Pilih Kolom --"] + kolom_tampil, key=f"del_sel_{tabel_id}", label_visibility="collapsed", disabled=not is_active)
                    
                    if col_del_btn.button("Hapus", key=f"btn_del_{tabel_id}", use_container_width=True, disabled=not is_active):
                        if del_choice != "-- Pilih Kolom --":
                            nama_col = del_choice
                            st.session_state.koleksi_tabel[i]['history'] = st.session_state.koleksi_tabel[i]['history'][:st.session_state.koleksi_tabel[i]['history_index'] + 1]
                            
                            if nama_col == "Jumlah":
                                st.session_state.koleksi_tabel[i]['hapus_jumlah'] = True
                                if st.session_state.koleksi_tabel[i]['active_sort_col'] == "Jumlah":
                                    st.session_state.koleksi_tabel[i]['active_sort_col'] = kolom_numerik[0] if kolom_numerik else None
                            else:
                                st.session_state.koleksi_tabel[i]['kolom_numerik'].remove(nama_col)
                                del st.session_state.koleksi_tabel[i]['data'][nama_col]
                                if st.session_state.koleksi_tabel[i]['active_sort_col'] == nama_col:
                                    sisa_kolom = st.session_state.koleksi_tabel[i]['kolom_numerik']
                                    if sisa_kolom:
                                        st.session_state.koleksi_tabel[i]['active_sort_col'] = sisa_kolom[0]
                                    elif not st.session_state.koleksi_tabel[i].get('hapus_jumlah', False):
                                        st.session_state.koleksi_tabel[i]['active_sort_col'] = "Jumlah"
                            
                            st.session_state.koleksi_tabel[i]['history'].append({
                                'data': copy.deepcopy(st.session_state.koleksi_tabel[i]['data']),
                                'kolom_numerik': copy.deepcopy(st.session_state.koleksi_tabel[i]['kolom_numerik']),
                                'hapus_jumlah': st.session_state.koleksi_tabel[i].get('hapus_jumlah', False),
                                'active_sort_col': st.session_state.koleksi_tabel[i]['active_sort_col']
                            })
                            st.session_state.koleksi_tabel[i]['history_index'] += 1
                            simpan_data(st.session_state.koleksi_tabel)
                            st.session_state.pop('hasil_kmeans', None)
                            st.rerun()

            df = pd.DataFrame(tabel['data'])
            
            if list(df['Kecamatan']) != DAFTAR_KECAMATAN:
                df = df.set_index('Kecamatan').reindex(DAFTAR_KECAMATAN).reset_index()
                st.session_state.koleksi_tabel[i]['data'] = df.to_dict(orient='list')
                simpan_data(st.session_state.koleksi_tabel)
                tabel['data'] = st.session_state.koleksi_tabel[i]['data'] 
            
            if len(kolom_numerik) > 0:
                disabled_cols = ["Kecamatan"]
                edit_cols = ["Kecamatan"] + kolom_numerik
                if not hapus_jumlah:
                    df['Jumlah'] = df[kolom_numerik].sum(axis=1)
                    disabled_cols.append("Jumlah")
            else:
                disabled_cols = ["Kecamatan"]
                edit_cols = ["Kecamatan", "Jumlah"] if not hapus_jumlah else ["Kecamatan"]
                
            active_col = tabel['active_sort_col']
            render_cols = ["Kecamatan"] + kolom_tampil
            df_view = df[render_cols].sort_values(by=active_col, ascending=not tabel['panah_bawah']).reset_index(drop=True)
            
            # --- RENDER TABEL (HIDUP vs MATI) ---
            if is_active:
                # Tabel normal dan bisa diedit
                df_berwarna = beri_warna_tabel(df_view, tabel['warna'], tabel['panah_bawah'], target_col=active_col)
                edited_df = st.data_editor(df_berwarna, use_container_width=True, hide_index=True, disabled=disabled_cols, key=f"editor_{tabel_id}")
                
                df_kembali_standar = edited_df[edit_cols].set_index('Kecamatan').reindex(DAFTAR_KECAMATAN).reset_index()
                data_baru = df_kembali_standar.to_dict(orient='list')
                
                if data_baru != tabel['data']:
                    st.session_state.koleksi_tabel[i]['data'] = data_baru
                    if 'history' in st.session_state.koleksi_tabel[i] and st.session_state.koleksi_tabel[i]['history_index'] >= 0:
                        idx_hist = st.session_state.koleksi_tabel[i]['history_index']
                        st.session_state.koleksi_tabel[i]['history'][idx_hist]['data'] = copy.deepcopy(data_baru)
                    simpan_data(st.session_state.koleksi_tabel) 
                    st.session_state.pop('hasil_kmeans', None)
                    st.rerun()
            else:
                # --- PERBAIKAN: Gaya Redup (Grayscale/Dimmed) yang beradaptasi dengan Dark Mode ---
                def style_inactive(row):
                    # Background transparan sangat tipis dan warna abu-abu pada font agar terlihat seperti dinonaktifkan
                    return ['background-color: rgba(128, 128, 128, 0.05); color: #6c757d;' for _ in row]
                
                df_mati = df_view.style.apply(style_inactive, axis=1)
                st.dataframe(df_mati, use_container_width=True, hide_index=True)

            st.write("")