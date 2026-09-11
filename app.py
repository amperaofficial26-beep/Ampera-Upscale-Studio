"""
Ampera Upscale Studio — titik masuk aplikasi.

Struktur:
    app.py          → kerangka: tema, sidebar, router antar halaman
    ui.py           → CSS tema (latar gradient bergerak) + komponen tampilan
    analysis.py     → identitas & penilaian kualitas berkas
    presets.py      → katalog model + pemilih model
    pages_*.py      → isi tiap halaman
    enhance.py      → engine upscale (foto, video, tiling, ffmpeg)
"""

import streamlit as st

import pages_home
import pages_image
import pages_join
import pages_learn
import pages_video
import ui

st.set_page_config(
    page_title="Ampera Upscale Studio",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)
ui.inject_css()

PAGES = {
    "Home": pages_home,
    "Image Upscale": pages_image,
    "Video Upscale": pages_video,
    "Gabung ke Ampera": pages_join,
    "Pelajari Lebih Lanjut": pages_learn,
}

if "page" not in st.session_state:
    st.session_state.page = "Home"


def goto(name: str) -> None:
    """Pindah halaman dari dalam halaman (dipakai tombol ajakan di Home)."""
    st.session_state.page = name
    st.rerun()


# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown(
        '<div class="amp-side-brand">'
        '<span class="n">Ampera Upscale</span>'
        '<span class="t">Studio</span>'
        '</div>', unsafe_allow_html=True)

    choice = st.radio("Menu", list(PAGES), key="page",
                      label_visibility="collapsed")

    st.markdown(
        '<div class="amp-side-foot">'
        'Ampera Official 26<br>Lampung, Indonesia<br><br>'
        '© Ampera Upscale — 2026'
        '</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------- konten
page = PAGES[choice]
if choice == "Home":
    page.render(goto)
else:
    page.render()
