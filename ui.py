"""
Lapisan tampilan (styling + komponen kecil) untuk Ampera Enhance.

Dipisah dari app.py supaya logika UI tetap ringkas dan gampang diubah.
Prinsip desain: elegan & sederhana — satu warna aksen, banyak ruang kosong,
garis tipis, tanpa emoji berlebihan.
"""

import streamlit as st

CSS = """
<style>
/* ---------- dasar ---------- */
#MainMenu, footer, header [data-testid="stStatusWidget"] {visibility: hidden;}
header {height: 0rem;}

html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, Roboto,
                 "Helvetica Neue", Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
}

.block-container {
    max-width: 1080px;
    padding-top: 3.2rem;
    padding-bottom: 5rem;
}

/* ---------- brand / judul ---------- */
.amp-brand {
    display: flex;
    align-items: baseline;
    gap: .6rem;
    margin-bottom: .15rem;
}
.amp-brand h1 {
    font-size: 1.95rem;
    font-weight: 650;
    letter-spacing: -0.025em;
    margin: 0;
    color: #111827;
}
.amp-brand span {
    font-size: .74rem;
    font-weight: 500;
    letter-spacing: .09em;
    text-transform: uppercase;
    color: #9CA3AF;
}
.amp-sub {
    color: #6B7280;
    font-size: .93rem;
    margin: 0 0 1.6rem 0;
}

/* ---------- label kecil ---------- */
.amp-label {
    font-size: .7rem;
    font-weight: 600;
    letter-spacing: .09em;
    text-transform: uppercase;
    color: #9CA3AF;
    margin: 1.7rem 0 .55rem 0;
}

/* ---------- kartu ---------- */
.amp-card {
    border: 1px solid #ECECEF;
    border-radius: 14px;
    padding: 1.05rem 1.2rem;
    background: #FFFFFF;
}
.amp-note {
    border: 1px solid #ECECEF;
    border-left: 3px solid #111827;
    border-radius: 10px;
    padding: .8rem 1rem;
    background: #FAFAFB;
    color: #4B5563;
    font-size: .88rem;
    line-height: 1.55;
}

/* ---------- baris statistik ---------- */
.amp-stats {
    display: flex;
    flex-wrap: wrap;
    gap: 2.2rem;
    border: 1px solid #ECECEF;
    border-radius: 14px;
    padding: .95rem 1.25rem;
    background: #FFFFFF;
}
.amp-stat .k {
    font-size: .68rem;
    font-weight: 600;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: #9CA3AF;
    margin-bottom: .18rem;
}
.amp-stat .v {
    font-size: 1.02rem;
    font-weight: 600;
    color: #111827;
    font-variant-numeric: tabular-nums;
}

/* ---------- radio jadi "pill" ---------- */
div[role="radiogroup"] {gap: .45rem;}
div[role="radiogroup"] > label {
    border: 1px solid #ECECEF;
    border-radius: 11px;
    padding: .62rem .85rem;
    background: #FFFFFF;
    transition: border-color .15s ease, background .15s ease;
}
div[role="radiogroup"] > label:hover {
    border-color: #D1D5DB;
    background: #FAFAFB;
}
div[role="radiogroup"] > label > div:first-child {display: none;}
div[role="radiogroup"] > label p {
    font-size: .91rem !important;
    color: #374151;
    margin: 0;
}
div[role="radiogroup"] > label:has(input:checked) {
    border-color: #111827;
    background: #F7F7F8;
}
div[role="radiogroup"] > label:has(input:checked) p {
    color: #111827;
    font-weight: 600;
}

/* ---------- tombol ---------- */
.stButton > button, .stDownloadButton > button {
    border-radius: 11px;
    font-weight: 550;
    font-size: .92rem;
    padding: .58rem 1.1rem;
    border: 1px solid #E5E7EB;
    transition: all .15s ease;
}
.stButton > button[kind="primary"] {
    background: #111827;
    border-color: #111827;
}
.stButton > button[kind="primary"]:hover:not(:disabled) {
    background: #000000;
    border-color: #000000;
}
.stButton > button:hover:not(:disabled),
.stDownloadButton > button:hover {
    border-color: #111827;
}

/* ---------- uploader ---------- */
[data-testid="stFileUploaderDropzone"] {
    border: 1px dashed #D8D8DE;
    border-radius: 14px;
    background: #FAFAFB;
    padding: 1.4rem;
    transition: border-color .15s ease;
}
[data-testid="stFileUploaderDropzone"]:hover {border-color: #111827;}

/* ---------- lain-lain ---------- */
[data-testid="stImage"] img {border-radius: 12px;}
[data-testid="stVideo"] video {border-radius: 12px;}
.stProgress > div > div > div > div {background-color: #111827;}
[data-testid="stExpander"] {
    border: 1px solid #ECECEF;
    border-radius: 12px;
    box-shadow: none;
}
[data-testid="stExpander"] summary p {font-size: .88rem; color: #4B5563;}
hr {margin: 2.2rem 0; border-color: #F0F0F2;}
[data-testid="stCaptionContainer"] p {color: #9CA3AF; font-size: .82rem;}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def brand(title: str, tag: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="amp-brand"><h1>{title}</h1><span>{tag}</span></div>'
        f'<p class="amp-sub">{subtitle}</p>',
        unsafe_allow_html=True)


def label(text: str) -> None:
    """Label seksi kecil bergaya uppercase."""
    st.markdown(f'<div class="amp-label">{text}</div>', unsafe_allow_html=True)


def stats(pairs) -> None:
    """Baris statistik ringkas: pairs = [(judul, nilai), ...]."""
    cells = "".join(
        f'<div class="amp-stat"><div class="k">{k}</div><div class="v">{v}</div></div>'
        for k, v in pairs)
    st.markdown(f'<div class="amp-stats">{cells}</div>', unsafe_allow_html=True)


def note(text: str) -> None:
    st.markdown(f'<div class="amp-note">{text}</div>', unsafe_allow_html=True)


def human_time(seconds: float) -> str:
    """Durasi enak dibaca: 'kurang dari 1 detik', '8 detik', '2,5 menit', '1,2 jam'."""
    if seconds < 1:
        return "kurang dari 1 detik"
    if seconds < 60:
        return f"{seconds:.0f} detik"
    if seconds < 3600:
        return f"{seconds / 60:.1f}".replace(".", ",") + " menit"
    return f"{seconds / 3600:.1f}".replace(".", ",") + " jam"


def human_size(num_bytes: float) -> str:
    """Ukuran berkas enak dibaca: '820 B', '4,3 KB', '18,2 MB'."""
    num_bytes = float(num_bytes or 0)
    if num_bytes < 1024:
        return f"{num_bytes:.0f} B"
    kb = num_bytes / 1024
    if kb < 1024:
        return f"{kb:.1f}".replace(".", ",") + " KB"
    return f"{kb / 1024:.1f}".replace(".", ",") + " MB"
