"""
Lapisan tampilan (styling + komponen kecil) untuk Ampera Upscale Studio.

Dipisah dari halaman supaya logika UI tetap ringkas dan gampang diubah.
Prinsip desain: elegan & sederhana — latar gradient charcoal/abu bergerak,
garis tipis, aksen tunggal, tanpa emoji berlebihan.
"""

import random

import streamlit as st

# ---------------------------------------------------------------- palet
CHARCOAL = "#1B1E23"
CHARCOAL_2 = "#23272E"
GRAY = "#3A4048"
ACCENT = "#E6E9EF"
MUTED = "#9BA3AF"

CSS = f"""
<style>
/* ============ latar gradient charcoal & abu yang bergerak ============ */
@keyframes ampShift {{
    0%   {{background-position:   0% 50%;}}
    50%  {{background-position: 100% 50%;}}
    100% {{background-position:   0% 50%;}}
}}
@keyframes ampFloat {{
    0%   {{transform: translate3d(0,0,0)        scale(1);}}
    33%  {{transform: translate3d(3vw,-4vh,0)   scale(1.08);}}
    66%  {{transform: translate3d(-3vw,3vh,0)   scale(0.95);}}
    100% {{transform: translate3d(0,0,0)        scale(1);}}
}}

.stApp {{
    background: linear-gradient(-45deg, #15181C, {CHARCOAL}, #2B313A, {GRAY}, #1E2228);
    background-size: 400% 400%;
    animation: ampShift 26s ease infinite;
}}
/* dua "lampu" abu yang mengambang pelan di belakang konten */
.stApp::before, .stApp::after {{
    content: "";
    position: fixed;
    border-radius: 50%;
    filter: blur(90px);
    pointer-events: none;
    z-index: 0;
}}
.stApp::before {{
    width: 46vw; height: 46vw;
    top: -12vh; left: -8vw;
    background: radial-gradient(circle, rgba(120,132,148,.22), transparent 70%);
    animation: ampFloat 34s ease-in-out infinite;
}}
.stApp::after {{
    width: 40vw; height: 40vw;
    bottom: -14vh; right: -6vw;
    background: radial-gradient(circle, rgba(88,96,110,.20), transparent 70%);
    animation: ampFloat 42s ease-in-out infinite reverse;
}}
/* Konten HARUS berada di atas dua blob ber-blur. Tanpa aturan ini blob
   (posisi fixed, z-index 0) menimpa gambar sehingga pratinjau tampak gelap. */
[data-testid="stMain"],
[data-testid="stSidebar"],
[data-testid="stHeader"] {{position: relative; z-index: 1;}}

/* hormati preferensi "kurangi animasi" */
@media (prefers-reduced-motion: reduce) {{
    .stApp, .stApp::before, .stApp::after {{animation: none !important;}}
}}

/* ============ dasar ============ */
#MainMenu, footer, header [data-testid="stStatusWidget"] {{visibility: hidden;}}
header {{background: transparent !important; height: 0rem;}}

html, body, [class*="css"] {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, Roboto,
                 "Helvetica Neue", Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
}}
.block-container {{max-width: 1080px; padding-top: 2.6rem; padding-bottom: 4rem;}}

/* ============ sidebar ============ */
[data-testid="stSidebar"] {{
    background: rgba(20,23,27,.86);
    backdrop-filter: blur(14px);
    border-right: 1px solid rgba(255,255,255,.07);
}}
[data-testid="stSidebar"] .block-container {{padding-top: 1.6rem;}}
[data-testid="stSidebarNav"] {{display: none;}}

.amp-side-brand {{
    display: flex; flex-direction: column; gap: .18rem;
    padding: .2rem .2rem 1.1rem .2rem;
    border-bottom: 1px solid rgba(255,255,255,.08);
    margin-bottom: 1.1rem;
}}
.amp-side-brand .n {{
    font-size: 1.06rem; font-weight: 650; color: {ACCENT};
    letter-spacing: -.02em;
}}
.amp-side-brand .t {{
    font-size: .64rem; font-weight: 500; letter-spacing: .14em;
    text-transform: uppercase; color: {MUTED};
}}

/* menu sidebar = radio bergaya nav */
[data-testid="stSidebar"] div[role="radiogroup"] {{gap: .3rem;}}
[data-testid="stSidebar"] div[role="radiogroup"] > label {{
    border: 1px solid transparent;
    border-radius: 10px;
    padding: .58rem .8rem;
    background: transparent;
    transition: all .16s ease;
}}
[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {{
    background: rgba(255,255,255,.05);
}}
[data-testid="stSidebar"] div[role="radiogroup"] > label p {{
    font-size: .9rem !important; color: #C3C9D2; margin: 0;
}}
[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {{
    background: rgba(255,255,255,.09);
    border-color: rgba(255,255,255,.14);
}}
[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) p {{
    color: #FFFFFF; font-weight: 600;
}}
.amp-side-foot {{
    margin-top: 1.4rem; padding-top: 1rem;
    border-top: 1px solid rgba(255,255,255,.08);
    font-size: .72rem; color: #737B87; line-height: 1.6;
}}

/* ============ brand halaman ============ */
.amp-brand {{display: flex; align-items: baseline; gap: .6rem; margin-bottom: .15rem;}}
.amp-brand h1 {{
    font-size: 1.9rem; font-weight: 650; letter-spacing: -.025em;
    margin: 0; color: {ACCENT};
}}
.amp-brand span {{
    font-size: .7rem; font-weight: 500; letter-spacing: .12em;
    text-transform: uppercase; color: {MUTED};
}}
.amp-sub {{color: #A8B0BC; font-size: .93rem; margin: 0 0 1.5rem 0;}}

/* ============ label seksi ============ */
.amp-label {{
    font-size: .68rem; font-weight: 600; letter-spacing: .12em;
    text-transform: uppercase; color: {MUTED}; margin: 1.6rem 0 .5rem 0;
}}

/* ============ kartu & catatan ============ */
.amp-card {{
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 14px; padding: 1.15rem 1.3rem;
    background: rgba(35,39,46,.55); backdrop-filter: blur(8px);
}}
.amp-note {{
    border: 1px solid rgba(255,255,255,.08);
    border-left: 3px solid #8A93A2;
    border-radius: 10px; padding: .8rem 1rem;
    background: rgba(35,39,46,.5);
    color: #B4BCC7; font-size: .88rem; line-height: 1.6;
}}

/* ============ baris statistik ============ */
.amp-stats {{
    display: flex; flex-wrap: wrap; gap: 2rem;
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 14px; padding: .95rem 1.25rem;
    background: rgba(35,39,46,.55); backdrop-filter: blur(8px);
}}
.amp-stat .k {{
    font-size: .64rem; font-weight: 600; letter-spacing: .1em;
    text-transform: uppercase; color: {MUTED}; margin-bottom: .2rem;
}}
.amp-stat .v {{
    font-size: 1rem; font-weight: 600; color: {ACCENT};
    font-variant-numeric: tabular-nums;
}}

/* ============ tabel identitas ============ */
.amp-idt {{
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 14px; overflow: hidden;
    background: rgba(35,39,46,.5);
}}
.amp-idt .row {{
    display: flex; justify-content: space-between; gap: 1rem;
    padding: .55rem .95rem;
    border-bottom: 1px solid rgba(255,255,255,.05);
    font-size: .865rem;
}}
.amp-idt .row:last-child {{border-bottom: none;}}
.amp-idt .row:nth-child(odd) {{background: rgba(255,255,255,.018);}}
.amp-idt .k {{color: {MUTED};}}
.amp-idt .v {{color: #DDE2E9; font-weight: 550; text-align: right;
             font-variant-numeric: tabular-nums; word-break: break-word;}}

/* ============ metrik kualitas ============ */
.amp-q {{display: flex; flex-wrap: wrap; gap: .55rem;}}
.amp-chip {{
    display: flex; flex-direction: column; gap: .16rem;
    border: 1px solid rgba(255,255,255,.09);
    border-radius: 11px; padding: .55rem .8rem;
    background: rgba(35,39,46,.6); min-width: 8.5rem;
}}
.amp-chip .k {{
    font-size: .62rem; letter-spacing: .1em; text-transform: uppercase;
    color: {MUTED}; font-weight: 600;
}}
.amp-chip .v {{font-size: .92rem; font-weight: 620;}}
.amp-chip .n {{font-size: .7rem; color: #7E8794; font-variant-numeric: tabular-nums;}}
.amp-chip.good .v {{color: #86D8A8;}}
.amp-chip.warn .v {{color: #E4C978;}}
.amp-chip.bad  .v {{color: #E79191;}}

/* ============ skor ============ */
.amp-score {{
    display: flex; align-items: center; gap: 1rem;
    border: 1px solid rgba(255,255,255,.08); border-radius: 14px;
    padding: .9rem 1.2rem; background: rgba(35,39,46,.55);
}}
.amp-score .num {{
    font-size: 1.9rem; font-weight: 680; color: {ACCENT};
    font-variant-numeric: tabular-nums; line-height: 1;
}}
.amp-score .num small {{font-size: .8rem; color: {MUTED}; font-weight: 500;}}
.amp-score .txt {{font-size: .88rem; color: #B4BCC7; line-height: 1.5;}}

/* ============ radio pilihan model ============ */
div[role="radiogroup"] {{gap: .45rem;}}
[data-testid="stMain"] div[role="radiogroup"] > label {{
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 11px; padding: .62rem .85rem;
    background: rgba(35,39,46,.45);
    transition: all .16s ease;
}}
[data-testid="stMain"] div[role="radiogroup"] > label:hover {{
    border-color: rgba(255,255,255,.2); background: rgba(45,50,58,.6);
}}
[data-testid="stMain"] div[role="radiogroup"] > label > div:first-child {{
    display: none;
}}
[data-testid="stMain"] div[role="radiogroup"] > label p {{
    font-size: .9rem !important; color: #BFC6D0; margin: 0;
}}
[data-testid="stMain"] div[role="radiogroup"] > label:has(input:checked) {{
    border-color: rgba(255,255,255,.32); background: rgba(58,64,72,.72);
}}
[data-testid="stMain"] div[role="radiogroup"] > label:has(input:checked) p {{
    color: #FFFFFF; font-weight: 600;
}}

/* ============ tombol ============ */
.stButton > button, .stDownloadButton > button {{
    border-radius: 11px; font-weight: 560; font-size: .92rem;
    padding: .6rem 1.15rem;
    border: 1px solid rgba(255,255,255,.14);
    background: rgba(45,50,58,.6); color: #E4E8EE;
    transition: all .16s ease;
}}
.stButton > button:hover:not(:disabled), .stDownloadButton > button:hover {{
    border-color: rgba(255,255,255,.34); background: rgba(60,66,76,.8);
    transform: translateY(-1px);
}}
.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, #E8EBF0, #B9C1CD);
    border-color: transparent; color: #14171B; font-weight: 650;
}}
.stButton > button[kind="primary"]:hover:not(:disabled) {{
    background: linear-gradient(135deg, #FFFFFF, #C9D1DC);
    box-shadow: 0 6px 20px rgba(0,0,0,.35);
}}

/* ============ uploader ============ */
[data-testid="stFileUploaderDropzone"] {{
    border: 1px dashed rgba(255,255,255,.18);
    border-radius: 14px; background: rgba(35,39,46,.45);
    padding: 1.4rem; transition: all .16s ease;
}}
[data-testid="stFileUploaderDropzone"]:hover {{
    border-color: rgba(255,255,255,.4); background: rgba(45,50,58,.55);
}}

/* ============ harga / paket ============ */
.amp-price {{
    border: 1px solid rgba(255,255,255,.1);
    border-radius: 16px; padding: 1.5rem 1.4rem;
    background: rgba(35,39,46,.62); backdrop-filter: blur(10px);
    height: 100%;
}}
.amp-price.hi {{
    border-color: rgba(255,255,255,.28);
    background: rgba(48,54,63,.7);
    box-shadow: 0 10px 34px rgba(0,0,0,.3);
}}
.amp-price .tag {{
    display: inline-block; font-size: .6rem; letter-spacing: .12em;
    text-transform: uppercase; font-weight: 700; color: #14171B;
    background: linear-gradient(135deg,#E8EBF0,#B9C1CD);
    padding: .2rem .55rem; border-radius: 20px; margin-bottom: .7rem;
}}
.amp-price h4 {{
    margin: 0 0 .25rem 0; font-size: 1.05rem; font-weight: 650; color: {ACCENT};
}}
.amp-price .desc {{font-size: .82rem; color: {MUTED}; margin-bottom: .9rem;}}
.amp-price .amt {{
    font-size: 1.75rem; font-weight: 680; color: #FFFFFF; line-height: 1;
    font-variant-numeric: tabular-nums;
}}
.amp-price .per {{font-size: .78rem; color: {MUTED}; font-weight: 500;}}
.amp-price .was {{
    font-size: .8rem; color: #6E7783; text-decoration: line-through;
    margin-top: .25rem;
}}
.amp-price ul {{margin: 1rem 0 0 0; padding-left: 1.05rem;}}
.amp-price li {{font-size: .855rem; color: #B4BCC7; margin-bottom: .38rem; line-height: 1.5;}}

/* ============ hero (Home) ============ */
.amp-hero {{padding: 2.4rem 0 .6rem 0; text-align: center;}}
.amp-hero .eyebrow {{
    font-size: .66rem; letter-spacing: .18em; text-transform: uppercase;
    color: {MUTED}; font-weight: 600; margin-bottom: .9rem;
}}
.amp-hero h1 {{
    font-size: 2.7rem; font-weight: 700; letter-spacing: -.035em;
    line-height: 1.14; margin: 0 0 .9rem 0;
    background: linear-gradient(120deg, #FFFFFF 10%, #A9B2BF 90%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}}
.amp-hero p {{
    font-size: 1.02rem; color: #A8B0BC; max-width: 34rem;
    margin: 0 auto; line-height: 1.65;
}}
.amp-feat {{
    border: 1px solid rgba(255,255,255,.07); border-radius: 14px;
    padding: 1.1rem 1.2rem; background: rgba(35,39,46,.45); height: 100%;
}}
.amp-feat .t {{font-size: .95rem; font-weight: 620; color: {ACCENT}; margin-bottom: .3rem;}}
.amp-feat .d {{font-size: .84rem; color: {MUTED}; line-height: 1.55;}}

/* ============ footer ============ */
.amp-footer {{
    margin-top: 3.2rem; padding-top: 1.3rem;
    border-top: 1px solid rgba(255,255,255,.07);
    text-align: center; font-size: .8rem; color: #6E7783;
}}

/* ============ lain-lain ============ */
[data-testid="stImage"] img {{border-radius: 12px;}}
[data-testid="stVideo"] video {{border-radius: 12px;}}
.stProgress > div > div > div > div {{
    background: linear-gradient(90deg,#8A93A2,#E8EBF0);
}}
[data-testid="stExpander"] {{
    border: 1px solid rgba(255,255,255,.08); border-radius: 12px;
    background: rgba(35,39,46,.4); box-shadow: none;
}}
[data-testid="stExpander"] summary p {{font-size: .87rem; color: #B4BCC7;}}
hr {{margin: 2rem 0; border-color: rgba(255,255,255,.07);}}
[data-testid="stCaptionContainer"] p {{color: #7E8794; font-size: .81rem;}}
.stTabs [data-baseweb="tab-list"] {{gap: .3rem;}}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------- komponen
def brand(title: str, tag: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="amp-brand"><h1>{title}</h1><span>{tag}</span></div>'
        f'<p class="amp-sub">{subtitle}</p>', unsafe_allow_html=True)


def label(text: str) -> None:
    st.markdown(f'<div class="amp-label">{text}</div>', unsafe_allow_html=True)


def stats(pairs) -> None:
    cells = "".join(
        f'<div class="amp-stat"><div class="k">{k}</div><div class="v">{v}</div></div>'
        for k, v in pairs)
    st.markdown(f'<div class="amp-stats">{cells}</div>', unsafe_allow_html=True)


def note(text: str) -> None:
    st.markdown(f'<div class="amp-note">{text}</div>', unsafe_allow_html=True)


def identity_table(rows) -> None:
    """Tabel identitas: rows = [(label, nilai), ...]."""
    body = "".join(
        f'<div class="row"><span class="k">{k}</span><span class="v">{v}</span></div>'
        for k, v in rows)
    st.markdown(f'<div class="amp-idt">{body}</div>', unsafe_allow_html=True)


def quality_chips(metrics) -> None:
    """metrics = [(judul, label, angka, tone), ...] dengan tone good/warn/bad."""
    chips = "".join(
        f'<div class="amp-chip {tone}"><div class="k">{k}</div>'
        f'<div class="v">{v}</div><div class="n">{n}</div></div>'
        for k, v, n, tone in metrics)
    st.markdown(f'<div class="amp-q">{chips}</div>', unsafe_allow_html=True)


def score_box(score: int, text: str) -> None:
    st.markdown(
        f'<div class="amp-score"><div class="num">{score}<small>/100</small></div>'
        f'<div class="txt">{text}</div></div>', unsafe_allow_html=True)


def footer(text: str = "© Ampera Upscale — 2026") -> None:
    st.markdown(f'<div class="amp-footer">{text}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------- format
def human_time(seconds: float) -> str:
    """Durasi enak dibaca: 'kurang dari 1 detik', '8 detik', '2,5 menit'."""
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


def rupiah(amount: int) -> str:
    """Format rupiah: 149000 -> 'Rp149.000'."""
    return "Rp" + f"{amount:,}".replace(",", ".")


# ---------------------------------------------------------------- sapaan
GREETINGS = [
    ("Selamat datang kembali.", "Kenangan lama layak tampil sejernih ingatanmu."),
    ("Halo, senang bertemu lagi.", "Mari bikin foto lawasmu terlihat seperti baru."),
    ("Hai, sudah siap berkarya?", "Satu unggahan saja, biar kami yang urus sisanya."),
    ("Selamat berkreasi.", "Detail yang hilang, kami coba kembalikan."),
    ("Apa kabar hari ini?", "Ada kenangan yang ingin dipertajam?"),
    ("Senang kamu mampir.", "Foto buram bukan akhir dari sebuah cerita."),
    ("Mari mulai.", "Kualitas terbaik untuk momen paling berharga."),
    ("Halo, kreator.", "Waktunya memberi hidup baru pada arsip lamamu."),
]


def random_greeting() -> tuple:
    """Sapaan acak — berganti setiap kali halaman Home dibuka."""
    return random.choice(GREETINGS)
