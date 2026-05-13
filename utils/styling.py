# utils/styling.py
import pandas as pd

def konversi_hex_ke_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def beri_warna_tabel(df, warna_hex, arah_panah_bawah, target_col):
    """Memberikan background transparan HANYA pada kolom Kecamatan berdasarkan target_col"""
    r, g, b = konversi_hex_ke_rgb(warna_hex)
    nilai_min = df[target_col].min()
    nilai_max = df[target_col].max()

    def style_row(row):
        nilai = row[target_col]
        if nilai_max == nilai_min:
            opacity = 0.5 
        else:
            rasio = (nilai - nilai_min) / (nilai_max - nilai_min)
            if not arah_panah_bawah:
                rasio = 1.0 - rasio
            opacity = 0.1 + (rasio * 0.9)

        color_style = f'background-color: rgba({r}, {g}, {b}, {opacity}); font-weight: 600;'
        return [color_style if col == 'Kecamatan' else '' for col in df.columns]

    return df.style.apply(style_row, axis=1)