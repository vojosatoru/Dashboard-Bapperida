# views/tab3_kmeans/ai_core.py
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from utils.constants import KECAMATAN_KUDUS_MAP

def proses_kmeans(df_untuk_ai, df_master, fitur_terpilih, n_clusters, bobot_baru, sensitivitas):
    """Memproses algoritma K-Means dengan pembobotan, sensitivitas, dan pengamanan error."""
    try:
        X = df_untuk_ai[fitur_terpilih]
        
        # --- FITUR 2: PENANGANAN ERROR AI (FALLBACK) ---
        # Mengecek apakah data terlalu seragam (angka sama semua di seluruh kecamatan)
        if X.std().sum() == 0:
            return None, "🚨 Data terlalu seragam (semua kecamatan nilainya sama). AI tidak dapat membedakan mana wilayah yang Kritis dan mana yang Aman. Silakan ubah bobot atau tambah indikator lain."
        
        # 1. Standarisasi Skala Data
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # 2. Terapkan Bobot (Weighting)
        X_scaled_weighted = X_scaled.copy()
        for i, fitur in enumerate(fitur_terpilih):
            weight = bobot_baru.get(fitur, 1.0)
            X_scaled_weighted[:, i] *= weight
            
        # 3. Terapkan Sensitivitas (Power Transformation)
        if sensitivitas > 1.0:
            X_scaled_weighted = np.sign(X_scaled_weighted) * (np.abs(X_scaled_weighted) ** sensitivitas)
        
        # 4. Proses Clustering K-Means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        klaster_mentah = kmeans.fit_predict(X_scaled_weighted)
        
        # 5. Sorting Centroid (Memastikan Klaster 0 = Aman, Klaster Terakhir = Sangat Kritis)
        rata_rata_klaster = []
        for i in range(n_clusters):
            rata_rata_klaster.append(X_scaled_weighted[klaster_mentah == i].mean())
        
        urutan_baru = {old_id: new_id for new_id, old_id in enumerate(np.argsort(rata_rata_klaster))}
        
        # 6. Memasukkan hasil ke DataFrame Master
        label_klaster = {0: "Zona 1 (Aman/Rendah)", 1: "Zona 2 (Waspada)", 2: "Zona 3 (Kritis)", 3: "Zona 4 (Sangat Kritis)"}
        
        df_master['Klaster_ID'] = [urutan_baru[k] for k in klaster_mentah]
        df_master['Status Zona'] = df_master['Klaster_ID'].map(label_klaster)
        df_master['Koordinat'] = df_master['Kecamatan'].map(KECAMATAN_KUDUS_MAP)
        
        return df_master, None # Mengembalikan df dan pesan error kosong
        
    except Exception as e:
        # Menangkap error bawaan sistem jika terjadi kegagalan matematis
        return None, f"🚨 Terjadi kesalahan matematis pada Mesin AI: {str(e)}"