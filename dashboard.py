# dashboard.py

from dash import Dash, html, dcc
# Dash: Kerangka utama aplikasi
# html: Untuk komponen HTML seperti judul (H1), paragraf (P), wadah (Div)
# dcc: Dash Core Components, untuk komponen interaktif seperti grafik (Graph), slider, dll.

# 1. Inisialisasi Aplikasi Dash
app = Dash(__name__)

# 2. Definisikan Tata Letak (Layout) Aplikasi
# 'app.layout' adalah "tubuh" dari halaman web Anda.
# Kita menggunakan html.Div untuk menampung semua elemen kita.
app.layout = html.Div(children=[
    # Komponen untuk judul utama halaman
    html.H1(
        children='Selamat Datang di Control Panel PLTN',
        style={'textAlign': 'center', 'color': '#FFFFFF'} # Sedikit styling
    ),

    # Komponen untuk sub-judul
    html.Div(
        children='Visualisasi dan Kontrol Reaktor Nuklir Berbasis AI',
        style={'textAlign': 'center', 'color': '#CCCCCC'}
    ),

    # Komponen untuk menampung grafik kita nanti
    # Untuk sekarang, ini hanya sebuah placeholder kosong.
    dcc.Graph(
        id='live-graph-display'
    )
], style={'backgroundColor': '#1E1E1E'}) # Memberi warna latar belakang gelap


# 3. Menjalankan Aplikasi
# Blok ini memungkinkan kita menjalankan server web lokal saat kita
# menjalankan skrip ini secara langsung.
if __name__ == '__main__':
    # debug=True sangat berguna selama pengembangan.
    # Server akan otomatis me-restart jika Anda menyimpan perubahan pada file.
    app.run(debug=True)