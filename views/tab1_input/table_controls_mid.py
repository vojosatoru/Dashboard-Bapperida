# views/tab1_input/table_controls_mid.py
import streamlit as st
import copy
from utils.state_manager import simpan_data

def render_mid_controls(i, tabel, kolom_tampil):
    """Menampilkan dan menangani aksi pada 4 kotak menu pengaturan tabel."""
    tabel_id = tabel['id']
    is_active = tabel.get('is_active', True)
    kolom_numerik = tabel['kolom_numerik']
    kolom_mati = tabel.get('kolom_mati', [])
    
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
            
            kolom_untuk_sort = [c for c in kolom_tampil if c not in kolom_mati]
            if not kolom_untuk_sort:
                kolom_untuk_sort = ["-- Kosong --"]
            
            sort_idx = kolom_untuk_sort.index(tabel.get('active_sort_col')) if tabel.get('active_sort_col') in kolom_untuk_sort else 0
            sort_choice = col_sort.selectbox("Pilih Kolom:", kolom_untuk_sort, index=sort_idx, key=f"sort_sel_{tabel_id}", label_visibility="collapsed", disabled=not is_active)
            
            dir_choice = col_dir.selectbox("Arah:", ["⬇️ Terbesar", "⬆️ Terkecil"], index=0 if tabel['panah_bawah'] else 1, key=f"dir_sel_{tabel_id}", label_visibility="collapsed", disabled=not is_active)
            is_panah_bawah = (dir_choice == "⬇️ Terbesar")
            
            if sort_choice != "-- Kosong --" and (sort_choice != tabel.get('active_sort_col') or is_panah_bawah != tabel['panah_bawah']):
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
        with st.expander("🗑️ Hapus / Matikan Kolom", expanded=False):
            st.markdown("**Kelola Indikator/Kolom:**")
            col_del_sel, col_off_btn, col_del_btn = st.columns([2, 1, 1])
            del_choice = col_del_sel.selectbox("Pilih Kolom:", ["-- Pilih Kolom --"] + kolom_tampil, key=f"del_sel_{tabel_id}", label_visibility="collapsed", disabled=not is_active)
            
            is_col_mati = del_choice in kolom_mati
            lbl_btn_mati = "🟢 Hidupkan" if is_col_mati else "⚫ Matikan"
            
            if col_off_btn.button(lbl_btn_mati, key=f"btn_off_{tabel_id}", use_container_width=True, disabled=(not is_active or del_choice == "-- Pilih Kolom --")):
                st.session_state.koleksi_tabel[i]['history'] = st.session_state.koleksi_tabel[i]['history'][:st.session_state.koleksi_tabel[i]['history_index'] + 1]
                
                if 'kolom_mati' not in st.session_state.koleksi_tabel[i]:
                    st.session_state.koleksi_tabel[i]['kolom_mati'] = []
                    
                if is_col_mati:
                    st.session_state.koleksi_tabel[i]['kolom_mati'].remove(del_choice)
                else:
                    st.session_state.koleksi_tabel[i]['kolom_mati'].append(del_choice)
                    if st.session_state.koleksi_tabel[i].get('active_sort_col') == del_choice:
                        valid_sort = [c for c in kolom_tampil if c not in st.session_state.koleksi_tabel[i]['kolom_mati']]
                        st.session_state.koleksi_tabel[i]['active_sort_col'] = valid_sort[0] if valid_sort else "Jumlah"
                
                st.session_state.koleksi_tabel[i]['history'].append({
                    'data': copy.deepcopy(st.session_state.koleksi_tabel[i]['data']),
                    'kolom_numerik': copy.deepcopy(st.session_state.koleksi_tabel[i]['kolom_numerik']),
                    'hapus_jumlah': st.session_state.koleksi_tabel[i].get('hapus_jumlah', False),
                    'active_sort_col': st.session_state.koleksi_tabel[i].get('active_sort_col', ''),
                    'kolom_mati': copy.deepcopy(st.session_state.koleksi_tabel[i]['kolom_mati'])
                })
                st.session_state.koleksi_tabel[i]['history_index'] += 1
                simpan_data(st.session_state.koleksi_tabel)
                st.session_state.pop('hasil_kmeans', None)
                st.rerun()

            if col_del_btn.button("Hapus", key=f"btn_del_{tabel_id}", use_container_width=True, disabled=not is_active):
                if del_choice != "-- Pilih Kolom --":
                    nama_col = del_choice
                    st.session_state.koleksi_tabel[i]['history'] = st.session_state.koleksi_tabel[i]['history'][:st.session_state.koleksi_tabel[i]['history_index'] + 1]
                    
                    if nama_col == "Jumlah":
                        st.session_state.koleksi_tabel[i]['hapus_jumlah'] = True
                        if st.session_state.koleksi_tabel[i].get('active_sort_col') == "Jumlah":
                            st.session_state.koleksi_tabel[i]['active_sort_col'] = kolom_numerik[0] if kolom_numerik else None
                    else:
                        st.session_state.koleksi_tabel[i]['kolom_numerik'].remove(nama_col)
                        del st.session_state.koleksi_tabel[i]['data'][nama_col]
                        if st.session_state.koleksi_tabel[i].get('active_sort_col') == nama_col:
                            sisa_kolom = st.session_state.koleksi_tabel[i]['kolom_numerik']
                            if sisa_kolom:
                                st.session_state.koleksi_tabel[i]['active_sort_col'] = sisa_kolom[0]
                            elif not st.session_state.koleksi_tabel[i].get('hapus_jumlah', False):
                                st.session_state.koleksi_tabel[i]['active_sort_col'] = "Jumlah"
                                
                    if 'kolom_mati' in st.session_state.koleksi_tabel[i] and nama_col in st.session_state.koleksi_tabel[i]['kolom_mati']:
                        st.session_state.koleksi_tabel[i]['kolom_mati'].remove(nama_col)
                    
                    st.session_state.koleksi_tabel[i]['history'].append({
                        'data': copy.deepcopy(st.session_state.koleksi_tabel[i]['data']),
                        'kolom_numerik': copy.deepcopy(st.session_state.koleksi_tabel[i]['kolom_numerik']),
                        'hapus_jumlah': st.session_state.koleksi_tabel[i].get('hapus_jumlah', False),
                        'active_sort_col': st.session_state.koleksi_tabel[i].get('active_sort_col', ''),
                        'kolom_mati': copy.deepcopy(st.session_state.koleksi_tabel[i].get('kolom_mati', []))
                    })
                    st.session_state.koleksi_tabel[i]['history_index'] += 1
                    simpan_data(st.session_state.koleksi_tabel)
                    st.session_state.pop('hasil_kmeans', None)
                    st.rerun()