# views/tab1_input/table_render.py
import streamlit as st
import streamlit.components.v1 as components
from views.tab1_input.backup_ui import render_backup_ui
from views.tab1_input.table_card import render_single_table

def render_tables():
    # Menampilkan fitur Ekspor / Impor JSON di bagian atas
    render_backup_ui()

    st.markdown("---")
    
    if not st.session_state.koleksi_tabel:
        st.info("Belum ada data yang ditambahkan. Klik '+ Tambah Data Baru' atau 'Auto Import' untuk memulai.")
    else:
        # Mengambil daftar semua judul tabel yang ada di memori
        daftar_judul = [t['judul'] for t in st.session_state.koleksi_tabel]
        
        # --- FITUR: SMART SEARCH AUTOCOMPLETE (INSTAN) ---
        search_query = st.multiselect(
            "🔍 Cari & Filter Tabel Indikator:", 
            options=daftar_judul,
            placeholder="Klik atau ketik judul tabel di sini...", 
            help="Tampilan akan langsung berubah seketika tanpa perlu menekan Enter. Anda juga bisa memilih beberapa tabel sekaligus."
        )
        
        # --- MENCEGAH BACKSPACE MENGHAPUS PILIHAN DI SEARCH BOX ---
        components.html(
            """
            <script>
            function cegahBackspace() {
                const doc = window.parent.document;
                const inputs = doc.querySelectorAll('[data-baseweb="select"] input');
                inputs.forEach(input => {
                    if (!input.dataset.kebalBackspace) {
                        input.addEventListener('keydown', function(e) {
                            if (e.key === 'Backspace' && this.value === '') {
                                e.stopPropagation();
                            }
                        }, true); 
                        input.dataset.kebalBackspace = 'true';
                    }
                });
            }
            
            cegahBackspace();
            const observer = new MutationObserver(() => {
                cegahBackspace();
            });
            observer.observe(window.parent.document.body, { childList: true, subtree: true });
            </script>
            """,
            height=0,
            width=0
        )
        
        st.caption("💡 Tip: Gunakan menu di bawah judul tabel untuk mengelola data dengan rapi.")
        
        # --- LOOPING & FILTERING TABEL ---
        for i, tabel in enumerate(st.session_state.koleksi_tabel):
            # Logika penyaringan instan: Tampilkan hanya tabel yang dipilih user
            if search_query and tabel['judul'] not in search_query:
                continue
                
            # Memanggil komponen tunggal untuk menggambar tabel yang lolos filter
            render_single_table(i, tabel)