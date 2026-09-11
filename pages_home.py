"""Halaman 1 — Home: sapaan berganti-ganti, ajakan mulai, footer."""

import streamlit as st

import ui


def render(goto):
    """goto(nama_halaman) dipakai tombol untuk pindah halaman."""
    # sapaan diacak setiap kali halaman Home dibuka (bukan setiap rerun,
    # supaya teks tidak berkedip saat tombol ditekan)
    if "greeting" not in st.session_state:
        st.session_state.greeting = ui.random_greeting()
    hello, tagline = st.session_state.greeting

    st.markdown(
        f"""
        <div class="amp-hero">
            <div class="eyebrow">Ampera Upscale Studio</div>
            <h1>{hello}</h1>
            <p>{tagline}</p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("Ayo tingkatkan kualitas kenangan indahmu",
                     type="primary", width="stretch", key="home_cta"):
            goto("Image Upscale")

    st.write("")
    st.write("")
    f1, f2, f3 = st.columns(3)
    feats = [
        ("Foto jadi tajam",
         "Model Real-ESRGAN dan Real-CUGAN mengembalikan detail yang hilang "
         "karena kompresi."),
        ("Video ikut naik kelas",
         "Diproses frame demi frame, audio asli tetap utuh, hasil siap diputar "
         "di mana saja."),
        ("Berjalan di server kami",
         "Berkasmu tidak dikirim ke layanan pihak ketiga dan tidak disimpan "
         "setelah selesai."),
    ]
    for col, (t, d) in zip((f1, f2, f3), feats):
        with col:
            st.markdown(
                f'<div class="amp-feat"><div class="t">{t}</div>'
                f'<div class="d">{d}</div></div>', unsafe_allow_html=True)

    st.write("")
    st.write("")
    ui.label("Cara kerjanya")
    ui.note(
        "<b>1.</b> Pilih menu <i>Image Upscale</i> atau <i>Video Upscale</i> di samping. &nbsp; "
        "<b>2.</b> Unggah berkasmu — kami tampilkan identitas dan penilaian kualitasnya. &nbsp; "
        "<b>3.</b> Pilih model yang cocok, lalu unduh hasilnya.")

    ui.footer("© Ampera Upscale — 2026")
