"""
Lapisan tampilan (CSS + komponen) untuk Ampera Upscale Studio.
Tema: gelap tenang & elegan, latar gradient bergerak, satu aksen perak.
"""

import random

import streamlit as st

BG = "#101214"
PANEL = "#171A1E"
PANEL_2 = "#1D2126"
ACCENT = "#E8EBEF"
MUTED = "#9AA2AD"
FAINT = "#6F7883"

CSS = f"""
<style>
@keyframes ampShift {{
    0%   {{background-position: 0% 50%;}}
    50%  {{background-position: 100% 50%;}}
    100% {{background-position: 0% 50%;}}
}}
@keyframes ampFloat {{
    0%   {{transform: translate3d(0,0,0) scale(1);}}
    33%  {{transform: translate3d(3vw,-4vh,0) scale(1.08);}}
    66%  {{transform: translate3d(-3vw,3vh,0) scale(.95);}}
    100% {{transform: translate3d(0,0,0) scale(1);}}
}}
@keyframes ampSweep {{
    0%   {{transform: translateX(-120%);}}
    100% {{transform: translateX(220%);}}
}}
@keyframes ampGlowPulse {{
    0%, 100% {{box-shadow: 0 0 0 1px rgba(255,255,255,.16),
                           0 0 10px -2px rgba(255,255,255,.16);}}
    50%      {{box-shadow: 0 0 0 1px rgba(255,255,255,.30),
                           0 0 20px -2px rgba(255,255,255,.34);}}
}}

/* ============ dasar ============ */
#MainMenu, footer, header [data-testid="stStatusWidget"] {{visibility: hidden;}}
header {{background: transparent !important; height: 0rem;}}
html, body, [class*="css"] {{
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI",
                 Roboto, "Helvetica Neue", Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
}}
.block-container {{max-width: 1000px; padding-top: 2.4rem; padding-bottom: 4rem;}}

/* ============ latar gradient bergerak + bola cahaya ============ */
.stApp {{
    background: linear-gradient(-45deg, #0D0F12, #16191D, #1D2126, #14171B, #101214);
    background-size: 400% 400%;
    animation: ampShift 26s ease infinite;
}}
.stApp::before, .stApp::after {{
    content: "";
    position: fixed;
    border-radius: 50%;
    filter: blur(90px);
    pointer-events: none;
    z-index: 0;
}}
.stApp::before {{
    width: 46vw; height: 46vw; top: -12vh; left: -8vw;
    background: radial-gradient(circle, rgba(120,132,148,.20), transparent 70%);
    animation: ampFloat 34s ease-in-out infinite;
}}
.stApp::after {{
    width: 40vw; height: 40vw; bottom: -14vh; right: -6vw;
    background: radial-gradient(circle, rgba(88,96,110,.18), transparent 70%);
    animation: ampFloat 42s ease-in-out infinite reverse;
}}
[data-testid="stAppViewContainer"] > .main {{position: relative; z-index: 1;}}
@media (prefers-reduced-motion: reduce) {{
    .stApp, .stApp::before, .stApp::after {{animation: none !important;}}
}}

/* ============ sidebar ============ */
[data-testid="stSidebar"] {{
    background: rgba(15,17,19,.92);
    backdrop-filter: blur(14px);
    border-right: 1px solid rgba(255,255,255,.06);
}}
[data-testid="stSidebar"] .block-container {{padding-top: 1.5rem;}}
[data-testid="stSidebarNav"] {{display: none;}}
.amp-side-brand {{
    padding: .25rem .25rem 1rem .25rem;
    border-bottom: 1px solid rgba(255,255,255,.07);
    margin-bottom: 1rem;
}}
.amp-side-brand .n {{
    display: block; font-size: 1.02rem; font-weight: 650; color: {ACCENT};
    letter-spacing: -.02em;
}}
.amp-side-brand .t {{
    display: block; margin-top: .18rem;
    font-size: .62rem; font-weight: 500; letter-spacing: .16em;
    text-transform: uppercase; color: {MUTED};
}}
[data-testid="stSidebar"] div[role="radiogroup"] {{gap: .25rem;}}
[data-testid="stSidebar"] div[role="radiogroup"] > label {{
    position: relative;
    overflow: hidden;
    border-radius: 9px;
    padding: .55rem .75rem .55rem .95rem;
    background: transparent;
    transition: background .15s ease;
}}
[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {{display: none;}}
[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {{background: rgba(255,255,255,.04);}}
[data-testid="stSidebar"] div[role="radiogroup"] > label p {{
    font-size: .9rem !important; color: #B7BEC8; margin: 0;
    position: relative; z-index: 1;
}}
[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {{
    background: rgba(255,255,255,.055);
    animation: ampGlowPulse 2.8s ease-in-out infinite;
}}
[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) p {{
    color: #FFFFFF; font-weight: 600;
}}
[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked)::after {{
    content: "";
    position: absolute; top: 0; bottom: 0; left: 0;
    width: 45%;
    background: linear-gradient(100deg,
        transparent 0%,
        rgba(255,255,255,.05) 35%,
        rgba(255,255,255,.30) 50%,
        rgba(255,255,255,.05) 65%,
        transparent 100%);
    filter: blur(3px);
    pointer-events: none;
    animation: ampSweep 3.4s ease-in-out infinite;
}}
.amp-side-foot {{
    margin-top: 1.4rem; padding-top: 1rem;
    border-top: 1px solid rgba(255,255,255,.06);
    font-size: .72rem; color: {FAINT}; line-height: 1.65;
}}

/* ============ kepala halaman ============ */
.amp-brand {{display: flex; align-items: baseline; gap: .6rem; margin-bottom: .35rem;}}
.amp-brand h1 {{
    font-size: 1.75rem; font-weight: 650; letter-spacing: -.025em;
    margin: 0; color: {ACCENT};
}}
.amp-brand span {{
    font-size: .66rem; font-weight: 500; letter-spacing: .14em;
    text-transform: uppercase; color: {MUTED};
}}
.amp-sub {{color: #A6ADB8; font-size: .92rem; margin: 0 0 1.75rem 0;}}

/* ============ label seksi ============ */
.amp-label {{
    font-size: .66rem; font-weight: 600; letter-spacing: .14em;
    text-transform: uppercase; color: {MUTED}; margin: 1.9rem 0 .65rem 0;
}}
.block-container .amp-label:first-child {{margin-top: 0;}}

/* ============ kartu & catatan ============ */
.amp-card {{
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 12px; padding: 1.1rem 1.25rem;
    background: rgba(23,26,30,.72); backdrop-filter: blur(8px);
}}
.amp-note {{
    border: 1px solid rgba(255,255,255,.07);
    border-left: 2px solid #7E8794;
    border-radius: 10px; padding: .8rem 1rem;
    background: rgba(23,26,30,.72); backdrop-filter: blur(8px);
    color: #AFB7C1; font-size: .88rem; line-height: 1.65;
}}

/* ============ baris statistik ============ */
.amp-stats {{
    display: flex; flex-wrap: wrap; gap: 1.6rem 2.4rem;
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 12px; padding: .95rem 1.25rem;
    background: rgba(23,26,30,.72); backdrop-filter: blur(8px);
}}
.amp-stat .k {{
    font-size: .62rem; font-weight: 600; letter-spacing: .1em;
    text-transform: uppercase; color: {MUTED}; margin-bottom: .22rem;
}}
.amp-stat .v {{
    font-size: .98rem; font-weight: 600; color: {ACCENT};
    font-variant-numeric: tabular-nums;
}}

/* ============ tabel identitas ============ */
.amp-idt {{
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 12px; overflow: hidden;
    background: rgba(23,26,30,.72);
}}
.amp-idt .row {{
    display: flex; justify-content: space-between; gap: 1rem;
    padding: .52rem .95rem;
    border-bottom: 1px solid rgba(255,255,255,.045);
    font-size: .855rem;
}}
.amp-idt .row:last-child {{border-bottom: none;}}
.amp-idt .row:nth-child(odd) {{background: rgba(255,255,255,.015);}}
.amp-idt .k {{color: {MUTED};}}
.amp-idt .v {{color: #D9DEE5; font-weight: 550; text-align: right;
             font-variant-numeric: tabular-nums; word-break: break-word;}}

/* ============ metrik kualitas ============ */
.amp-q {{display: flex; flex-wrap: wrap; gap: .5rem;}}
.amp-chip {{
    display: flex; flex-direction: column; gap: .14rem;
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 10px; padding: .5rem .75rem;
    background: rgba(23,26,30,.72); min-width: 8.2rem;
}}
.amp-chip .k {{
    font-size: .6rem; letter-spacing: .1em; text-transform: uppercase;
    color: {MUTED}; font-weight: 600;
}}
.amp-chip .v {{font-size: .9rem; font-weight: 620;}}
.amp-chip .n {{font-size: .68rem; color: {FAINT}; font-variant-numeric: tabular-nums;}}
.amp-chip.good .v {{color: #8AD3A9;}}
.amp-chip.warn .v {{color: #E3CD82;}}
.amp-chip.bad  .v {{color: #E59494;}}

/* ============ skor ============ */
.amp-score {{
    display: flex; align-items: center; gap: 1rem;
    border: 1px solid rgba(255,255,255,.07); border-radius: 12px;
    padding: .85rem 1.15rem; background: rgba(23,26,30,.72);
}}
.amp-score .num {{
    font-size: 1.8rem; font-weight: 680; color: {ACCENT};
    font-variant-numeric: tabular-nums; line-height: 1;
}}
.amp-score .num small {{font-size: .78rem; color: {MUTED}; font-weight: 500;}}
.amp-score .txt {{font-size: .87rem; color: #AFB7C1; line-height: 1.55;}}

/* ============ pilihan model (radio) ============ */
div[role="radiogroup"] > label > div:first-child {{display: none;}}
div[role="radiogroup"] {{gap: .45rem;}}
[data-testid="stMain"] div[role="radiogroup"] > label {{
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 10px; padding: .6rem .85rem;
    background: rgba(23,26,30,.72);
    transition: border-color .15s ease, background .15s ease;
}}
[data-testid="stMain"] div[role="radiogroup"] > label:hover {{border-color: rgba(255,255,255,.16);}}
[data-testid="stMain"] div[role="radiogroup"] > label p {{
    font-size: .9rem !important; color: #BCC3CD; margin: 0;
    position: relative; z-index: 1;
}}
[data-testid="stMain"] div[role="radiogroup"] > label:has(input:checked) {{
    border-color: rgba(255,255,255,.32); background: rgba(29,33,38,.85);
    animation: ampGlowPulse 2.8s ease-in-out infinite;
}}
[data-testid="stMain"] div[role="radiogroup"] > label:has(input:checked) p {{color: #FFFFFF;}}
[data-testid="stMain"] div[role="radiogroup"] > label:has(input:checked) p strong {{color: #FFFFFF;}}
[data-testid="stMain"] div[role="radiogroup"] > label:has(input:checked)::after {{
    content: "";
    position: absolute; top: 0; bottom: 0; left: 0;
    width: 40%;
    background: linear-gradient(100deg,
        transparent 0%,
        rgba(255,255,255,.05) 35%,
        rgba(255,255,255,.26) 50%,
        rgba(255,255,255,.05) 65%,
        transparent 100%);
    filter: blur(3px);
    pointer-events: none;
    animation: ampSweep 3.4s ease-in-out infinite;
}}
/* ============ tombol ============ */
.stButton > button, .stDownloadButton > button {{
    border-radius: 10px; font-weight: 560; font-size: .92rem;
    padding: .58rem 1.15rem;
    border: 1px solid rgba(255,255,255,.13);
    background: rgba(255,255,255,.035); color: #DFE4EA;
    transition: background .15s ease, border-color .15s ease;
}}
.stButton > button:hover:not(:disabled), .stDownloadButton > button:hover {{
    border-color: rgba(255,255,255,.28); background: rgba(255,255,255,.07);
}}
.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"] {{
    background: {ACCENT}; border-color: transparent; color: #14171B;
    font-weight: 650;
}}
.stButton > button[kind="primary"]:hover:not(:disabled) {{background: #FFFFFF;}}

/* ============ uploader ============ */
[data-testid="stFileUploaderDropzone"] {{
    border: 1px dashed rgba(255,255,255,.16);
    border-radius: 12px; background: rgba(255,255,255,.02);
    padding: 1.35rem; transition: border-color .15s ease, background .15s ease;
}}
[data-testid="stFileUploaderDropzone"]:hover {{
    border-color: rgba(255,255,255,.32); background: rgba(255,255,255,.04);
}}

/* ============ harga / paket ============ */
.amp-price {{
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 14px; padding: 1.45rem 1.35rem;
    background: rgba(23,26,30,.78); backdrop-filter: blur(10px);
    height: 100%;
}}
.amp-price.hi {{border-color: rgba(255,255,255,.24); background: rgba(29,33,38,.85);}}
.amp-price .tag {{
    display: inline-block; font-size: .6rem; letter-spacing: .12em;
    text-transform: uppercase; font-weight: 700; color: #14171B;
    background: {ACCENT};
    padding: .18rem .55rem; border-radius: 20px; margin-bottom: .7rem;
}}
.amp-price h4 {{margin: 0 0 .25rem 0; font-size: 1.02rem; font-weight: 650; color: {ACCENT};}}
.amp-price .desc {{font-size: .82rem; color: {MUTED}; margin-bottom: .9rem;}}
.amp-price .amt {{
    font-size: 1.7rem; font-weight: 680; color: #FFFFFF; line-height: 1;
    font-variant-numeric: tabular-nums;
}}
.amp-price .per {{font-size: .78rem; color: {MUTED}; font-weight: 500;}}
.amp-price .was {{font-size: .8rem; color: {FAINT}; text-decoration: line-through; margin-top: .25rem;}}
.amp-price ul {{margin: 1rem 0 0 0; padding-left: 1.05rem;}}
.amp-price li {{font-size: .845rem; color: #AFB7C1; margin-bottom: .38rem; line-height: 1.5;}}

/* ============ hero (Beranda) ============ */
.amp-hero {{padding: 2.2rem 0 .5rem 0; text-align: center;}}
.amp-hero .eyebrow {{
    font-size: .64rem; letter-spacing: .18em; text-transform: uppercase;
    color: {MUTED}; font-weight: 600; margin-bottom: .95rem;
}}
.amp-hero h1 {{
    font-size: 2.5rem; font-weight: 700; letter-spacing: -.03em;
    line-height: 1.15; margin: 0 0 .9rem 0;
    background: linear-gradient(120deg, #FFFFFF 20%, #A7AFBB 90%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}}
.amp-hero p {{
    font-size: 1rem; color: #A6ADB8; max-width: 33rem;
    margin: 0 auto; line-height: 1.65;
}}
.amp-feat {{
    border: 1px solid rgba(255,255,255,.07); border-radius: 12px;
    padding: 1.05rem 1.15rem; background: rgba(23,26,30,.72);
    backdrop-filter: blur(8px); height: 100%;
}}
.amp-feat .t {{font-size: .93rem; font-weight: 620; color: {ACCENT}; margin-bottom: .3rem;}}
.amp-feat .d {{font-size: .84rem; color: {MUTED}; line-height: 1.55;}}

/* ============ footer ============ */
.amp-footer {{
    margin-top: 3rem; padding-top: 1.25rem;
    border-top: 1px solid rgba(255,255,255,.06);
    text-align: center; font-size: .79rem; color: {FAINT};
}}

/* ============ lain-lain ============ */
[data-testid="stImage"] img {{border-radius: 10px;}}
[data-testid="stVideo"] video {{border-radius: 10px;}}
.stProgress > div > div > div > div {{background: {ACCENT};}}
[data-testid="stExpander"] {{
    border: 1px solid rgba(255,255,255,.07); border-radius: 10px;
    background: rgba(23,26,30,.72); box-shadow: none;
}}
[data-testid="stExpander"] summary p {{font-size: .87rem; color: #AFB7C1;}}
hr {{margin: 1.75rem 0; border-color: rgba(255,255,255,.06);}}
[data-testid="stCaptionContainer"] p {{color: {FAINT}; font-size: .8rem;}}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def brand(title: str, tag: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="amp-brand"><h1>{title}</h1><span>{tag}</span></div>'
        f'<p class="amp-sub">{subtitle}</p>', unsafe_allow_html=True)


def label(text: str) -> None:
    st.markdown(f'<div class="amp-label">{text}</div>', unsafe_allow_html=True)


def hero(eyebrow: str, title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="amp-hero">'
        f'<div class="eyebrow">{eyebrow}</div>'
        f'<h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


def stats(pairs) -> None:
    cells = "".join(
        f'<div class="amp-stat"><div class="k">{k}</div><div class="v">{v}</div></div>'
        for k, v in pairs)
    st.markdown(f'<div class="amp-stats">{cells}</div>', unsafe_allow_html=True)


def note(text: str) -> None:
    st.markdown(f'<div class="amp-note">{text}</div>', unsafe_allow_html=True)


def identity_table(rows) -> None:
    body = "".join(
        f'<div class="row"><span class="k">{k}</span><span class="v">{v}</span></div>'
        for k, v in rows)
    st.markdown(f'<div class="amp-idt">{body}</div>', unsafe_allow_html=True)


def quality_chips(metrics) -> None:
    chips = "".join(
        f'<div class="amp-chip {tone}"><div class="k">{k}</div>'
        f'<div class="v">{v}</div><div class="n">{n}</div></div>'
        for k, v, n, tone in metrics)
    st.markdown(f'<div class="amp-q">{chips}</div>', unsafe_allow_html=True)


def score_box(score: int, text: str) -> None:
    st.markdown(
        f'<div class="amp-score"><div class="num">{score}<small>/100</small></div>'
        f'<div class="txt">{text}</div></div>', unsafe_allow_html=True)


def features(items) -> None:
    cols = st.columns(len(items))
    for col, (t, d) in zip(cols, items):
        with col:
            st.markdown(
                f'<div class="amp-feat"><div class="t">{t}</div>'
                f'<div class="d">{d}</div></div>', unsafe_allow_html=True)


def footer(text: str = "© Ampera Upscale — 2026") -> None:
    st.markdown(f'<div class="amp-footer">{text}</div>', unsafe_allow_html=True)


def human_time(seconds: float) -> str:
    if seconds < 1:
        return "kurang dari 1 detik"
    if seconds < 60:
        return f"{seconds:.0f} detik"
    if seconds < 3600:
        return f"{seconds / 60:.1f}".replace(".", ",") + " menit"
    return f"{seconds / 3600:.1f}".replace(".", ",") + " jam"


def human_size(num_bytes: float) -> str:
    num_bytes = float(num_bytes or 0)
    if num_bytes < 1024:
        return f"{num_bytes:.0f} B"
    kb = num_bytes / 1024
    if kb < 1024:
        return f"{kb:.1f}".replace(".", ",") + " KB"
    return f"{kb / 1024:.1f}".replace(".", ",") + " MB"


def rupiah(amount: int) -> str:
    return "Rp" + f"{amount:,}".replace(",", ".")


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
    return random.choice(GREETINGS)
