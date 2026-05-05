# views/tab1_input/backup_ui.py
import streamlit as st
import json
import requests
from utils.state_manager import simpan_data, muat_config_kmeans, simpan_config_kmeans

def kelola_gist(aksi, token, filename, content_string=None, gist_id=None):
    """Fungsi untuk Push/Pull data dari GitHub Gist agar tidak mengotori commit Repo utama."""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    if aksi == "PUSH":
        payload = {
            "description": "Auto-backup Data MURIA App",
            "public": False, # Rahasia, hanya bisa dilihat pemilik token
            "files": {
                filename: {
                    "content": content_string
                }
            }
        }
        if gist_id: # Update Gist yang sudah ada
            url = f"https://api.github.com/gists/{gist_id}"
            resp = requests.patch(url, headers=headers, json=payload)
            return resp.status_code == 200, resp.json()
        else: # Buat Gist baru
            url = "https://api.github.com/gists"
            resp = requests.post(url, headers=headers, json=payload)
            return resp.status_code == 201, resp.json()
            
    elif aksi == "PULL":
        if not gist_id:
            return False, {"message": "Gist ID diperlukan untuk mengambil data."}
        url = f"https://api.github.com/gists/{gist_id}"
        resp = requests.get(url, headers=headers)
        return resp.status_code == 200, resp.json()

def render_backup_ui():
    """Merender antarmuka expander untuk Ekspor/Impor Lokal & Cloud Backup"""
    with st.expander("💾 Simpan / Muat Proyek", expanded=False):
        st.info("💡 Gunakan fitur ini untuk mengamankan data secara lokal, atau Sinkronisasikan ke Cloud (GitHub Gist).")
        
        # --- PERBAIKAN: Menampilkan pesan sukses yang dititipkan di memori sebelum rerun ---
        if st.session_state.get('pesan_sukses_backup'):
            st.success(st.session_state.pesan_sukses_backup)
            # Menghapus pesan dari memori setelah ditampilkan agar tidak muncul terus-menerus
            st.session_state.pesan_sukses_backup = None

        # Menggabungkan data tabel (Tab 1) dan setingan AI (Tab 3) menjadi satu paket
        project_data = {
            "data_tabel": st.session_state.get('koleksi_tabel', []),
            "config_ai": muat_config_kmeans()
        }
        json_string = json.dumps(project_data, indent=4)
        current_key = st.session_state.get('project_key', 'publik')
        nama_file_unduh = f"Backup_{current_key.capitalize()}.json"
        
        # --- TAB MANAJEMEN DATA ---
        # Menukar posisi: Cloud Backup menjadi tab pertama, Penyimpanan Lokal menjadi tab kedua
        tab_cloud, tab_lokal = st.tabs(["☁️ Cloud Backup (1-Click Sync)", "💻 Penyimpanan Lokal"])
        
        with tab_cloud:
            st.markdown("**Sinkronisasi Data Permanen (Cloud Database)**")
            
            # --- MENGAMBIL TOKEN & GIST ID DARI SECRETS (TERSEMBUNYI DARI UI) ---
            gh_token = ""
            gh_gist = ""
            try:
                if "GITHUB_TOKEN" in st.secrets:
                    gh_token = st.secrets["GITHUB_TOKEN"]
                if "GIST_ID" in st.secrets:
                    gh_gist = st.secrets["GIST_ID"]
            except Exception:
                pass # Abaikan secara diam-diam jika file secrets.toml tidak ada
            
            # Peringatan jika secrets belum disetting
            if not gh_token or not gh_gist:
                st.warning("⚠️ Konfigurasi Cloud belum terdeteksi. Pastikan variabel 'GITHUB_TOKEN' dan 'GIST_ID' sudah ditambahkan di menu Secrets Streamlit.")
            
            col_push, col_pull = st.columns(2)
            
            # AKSI 1: PUSH
            if col_push.button("🚀 PUSH (Simpan Perubahan ke Cloud)", type="primary", use_container_width=True, disabled=(not gh_token or not gh_gist)):
                with st.spinner(f"Sedang mengunggah data {current_key.capitalize()} ke Cloud..."):
                    sukses, respon_api = kelola_gist(
                        aksi="PUSH",
                        token=gh_token.strip(),
                        filename=nama_file_unduh,
                        content_string=json_string,
                        gist_id=gh_gist.strip()
                    )
                    if sukses:
                        st.success(f"✅ Berhasil! Data Ruang '{current_key.capitalize()}' telah tersimpan aman di Cloud.")
                    else:
                        st.error(f"❌ Gagal Push. Cek konfigurasi Token/Secrets Anda.\nDetail: {respon_api.get('message', 'Unknown Error')}")

            # AKSI 2: PULL
            if col_pull.button("📥 PULL (Muat Data dari Cloud)", use_container_width=True, disabled=(not gh_token or not gh_gist)):
                with st.spinner(f"Sedang mengunduh data {current_key.capitalize()} dari Cloud..."):
                    sukses, respon_api = kelola_gist(
                        aksi="PULL",
                        token=gh_token.strip(),
                        filename=nama_file_unduh,
                        gist_id=gh_gist.strip()
                    )
                    if sukses:
                        try:
                            files_dict = respon_api.get('files', {})
                            if nama_file_unduh not in files_dict:
                                st.error(f"❌ File '{nama_file_unduh}' belum pernah di-Push ke Cloud untuk ruang kerja ini.")
                            else:
                                konten_json_str = files_dict[nama_file_unduh].get('content', '')
                                isi_file = json.loads(konten_json_str)
                                
                                if "data_tabel" in isi_file:
                                    st.session_state.koleksi_tabel = isi_file["data_tabel"]
                                    simpan_data(isi_file["data_tabel"])
                                if "config_ai" in isi_file:
                                    simpan_config_kmeans(isi_file["config_ai"])
                                if 'hasil_kmeans' in st.session_state:
                                    del st.session_state['hasil_kmeans']
                                    
                                # Menitipkan pesan sukses ke memori sebelum rerun, lalu menghapus time.sleep()
                                st.session_state.pesan_sukses_backup = f"✅ Data Ruang '{current_key.capitalize()}' berhasil dipulihkan dari Cloud!"
                                st.rerun()
                        except Exception as e:
                            st.error(f"❌ Gagal memproses data JSON: {str(e)}")
                    else:
                        st.error(f"❌ Gagal Pull. Pastikan Token dan Gist ID di Secrets valid.\nDetail: {respon_api.get('message', 'Unknown Error')}")

        with tab_lokal:
            col_export, col_import = st.columns(2)
            with col_export:
                st.markdown("**1. Simpan Proyek (Ekspor Lokal)**")
                st.download_button(
                    label="📥 Unduh Proyek (.json)",
                    data=json_string,
                    file_name=nama_file_unduh,
                    mime="application/json",
                    use_container_width=True,
                    help=f"Unduh ke laptop Anda."
                )
                
            with col_import:
                st.markdown("**2. Lanjutkan Proyek (Impor Lokal)**")
                uploaded_project = st.file_uploader("Unggah File Proyek (.json)", type=['json'], label_visibility="collapsed")
                if uploaded_project is not None:
                    if st.button("🔄 Pulihkan Data Lokal", use_container_width=True, type="primary"):
                        try:
                            isi_file = json.load(uploaded_project)
                            if "data_tabel" in isi_file:
                                st.session_state.koleksi_tabel = isi_file["data_tabel"]
                                simpan_data(isi_file["data_tabel"])
                            if "config_ai" in isi_file:
                                simpan_config_kmeans(isi_file["config_ai"])
                            if 'hasil_kmeans' in st.session_state:
                                del st.session_state['hasil_kmeans']
                            
                            # Menitipkan pesan sukses ke memori sebelum rerun
                            st.session_state.pesan_sukses_backup = "✅ Proyek berhasil dipulihkan dari penyimpanan lokal!"
                            st.rerun()
                        except Exception as e:
                            st.error("❌ File tidak valid atau rusak.")