"""
Ampera Upscale Studio — titik masuk aplikasi.

Struktur:
    app.py          → kerangka: tema, sidebar, router antar halaman
    ui.py           → CSS tema (latar gelap tenang) + komponen tampilan
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
    "Beranda": pages_home,
    "Foto": pages_image,
    "Video": pages_video,
    "Keanggotaan": pages_join,
    "Panduan": pages_learn,
}
PAGE_ICONS = {
    "Beranda": ":material/home:",
    "Foto": ":material/image:",
    "Video": ":material/movie:",
    "Keanggotaan": ":material/workspace_premium:",
    "Panduan": ":material/menu_book:",
}

if "page" not in st.session_state:
    st.session_state.page = "Beranda"


def goto(name: str) -> None:
    """Callback navigasi — WAJIB dipanggil lewat on_click (bukan di badan
    script), karena state widget (key="page") hanya boleh diubah sebelum
    widget dibuat ulang di run berikutnya."""
    st.session_state.page = name


# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown(
        '<div class="amp-side-brand">'
        '<span class="n">Ampera Upscale</span>'
        '<span class="t">Studio</span>'
        '</div>', unsafe_allow_html=True)

    choice = st.radio("Menu", list(PAGES), key="page",
                      format_func=lambda p: f"{PAGE_ICONS.get(p, '')} {p}",
                      label_visibility="collapsed")

    st.markdown(
        '<div class="amp-side-foot">'
        'Ampera Official 26 · Palembang<br>'
        '© Ampera Upscale — 2026'
        '</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------- konten
page = PAGES[choice]
if choice == "Beranda":
    page.render(goto)
else:
    page.render()
