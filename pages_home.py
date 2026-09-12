"""Halaman 1 — Beranda: sapaan, ajakan mulai, ringkasan fitur, cara kerja."""

import streamlit as st

import ui


def render(goto=None):
    # sapaan diacak sekali per sesi, bukan tiap rerun, supaya teks tidak
    # berkedip saat halaman digambar ulang
    if "greeting" not in st.session_state:
        st.session_state.greeting = ui.random_greeting()
    hello, tagline = st.session_state.greeting

    ui.hero("Ampera Upscale Studio", hello, tagline)

    # ajakan utama — tombol sungguhan yang langsung memindah halaman
    # (navigasi lewat callback on_click; lihat catatan di app.py:goto)
    c1, c2 = st.columns(2)
    with c1:
        st.button("Perjelas foto", type="primary", width="stretch",
                  key="home_photo", on_click=goto, args=("Foto",))
    with c2:
        st.button("Perjelas video", width="stretch", key="home_video",
                  on_click=goto, args=("Video",))

    st.write("")
    ui.features([
        ("Foto jadi tajam",
         "Model Real-ESRGAN dan Real-CUGAN mengembalikan detail yang hilang "
         "karena kompresi."),
        ("Video ikut naik kelas",
         "Diproses frame demi frame, audio asli tetap utuh, hasil siap diputar "
         "di mana saja."),
        ("Aman dan tertutup",
         "Berkasmu tidak dikirim ke layanan pihak ketiga dan tidak disimpan "
         "setelah selesai."),
    ])

    ui.label("Cara kerjanya")
    ui.note(
        "<b>1.</b> Pilih menu <i>Foto</i> atau <i>Video</i> di samping. &nbsp;·&nbsp; "
        "<b>2.</b> Unggah berkasmu — kami tampilkan identitas dan penilaian kualitasnya. "
        "&nbsp;·&nbsp; "
        "<b>3.</b> Pilih model yang cocok, lalu unduh hasilnya.")

    ui.footer("© Ampera Upscale — 2026")
