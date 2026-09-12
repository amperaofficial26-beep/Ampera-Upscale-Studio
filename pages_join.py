"""
Halaman 4 — Gabung ke Ampera: profil Ampera Official 26 + paket berbayar.

Catatan: angka harga di bawah masih PLACEHOLDER — silakan ganti nilainya
di konstanta PRICE_* saat harga final sudah ditentukan.
"""

import streamlit as st

import ui

# --------------------------------------------------- harga (placeholder)
PRICE_YEAR = 49_000        # harga promo tahunan
PRICE_YEAR_WAS = 159_000    # harga coret
PRICE_MONTH = 19_000        # harga bulanan
PRICE_LIFETIME = 435_000    # sekali bayar


def render():
    ui.brand("Keanggotaan", "Gabung ke Ampera",
             "Satu keanggotaan, semua produk Ampera Official 26 terbuka untukmu.")

    # ---------------------------------------------- tentang
    ui.label("Tentang Ampera Official 26")
    st.markdown(
        """
        <div class="amp-card">
        <p style="margin:0 0 .8rem 0; color:#B4BCC7; font-size:.92rem; line-height:1.7;">
        <b style="color:#E6E9EF;">Ampera Official 26</b> adalah studio digital asal
        Palembang yang membangun perkakas kreatif ringan — cukup dijalankan lewat
        peramban, tanpa perlu komputer berspesifikasi tinggi. Kami percaya alat
        yang bagus seharusnya bisa dipakai siapa saja, termasuk dari laptop lama
        atau koneksi seadanya.
        </p>
        <p style="margin:0; color:#B4BCC7; font-size:.92rem; line-height:1.7;">
        <i>Ampera Upscale Studio</i> adalah produk Kedua kami: penajam foto dan
        video berbasis AI yang berjalan sepenuhnya di server sendiri. Berkasmu
        tidak pernah dikirim ke layanan pihak ketiga.
        </p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    m1, m2, m3, m4 = st.columns(4)
    for col, (k, v) in zip((m1, m2, m3, m4), [
            ("Berdiri", "2025"), ("Basis", "Palembang, ID"),
            ("Produk aktif", "2"), ("Model AI", "5")]):
        with col:
            st.markdown(
                f'<div class="amp-feat"><div class="d">{k}</div>'
                f'<div class="t" style="margin-top:.2rem">{v}</div></div>',
                unsafe_allow_html=True)

    # ---------------------------------------------- penawaran
    st.write("")
    ui.label("Pilih paketmu")
    st.markdown(
        f"""
        <div class="amp-note" style="margin-bottom:1rem;">
        <b style="color:#E6E9EF;">Gabung dan nikmati semua produk Ampera selama
        1 tahun dengan harga {ui.rupiah(PRICE_YEAR)}</b> — hemat
        {ui.rupiah(PRICE_YEAR_WAS - PRICE_YEAR)} dari harga normal
        {ui.rupiah(PRICE_YEAR_WAS)}. Berlaku untuk seluruh produk yang kami rilis
        selama masa keanggotaan.
        </div>
        """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"""
            <div class="amp-price">
                <h4>Bulanan</h4>
                <div class="desc">Coba dulu, bebas berhenti</div>
                <div class="amt">{ui.rupiah(PRICE_MONTH)}</div>
                <div class="per">per bulan</div>
                <ul>
                    <li>Semua model AI terbuka</li>
                    <li>Foto sampai 20 MB</li>
                    <li>Video sampai 10 detik</li>
                    <li>Tanpa tanda air</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    with c2:
        st.markdown(
            f"""
            <div class="amp-price hi">
                <div class="tag">Paling hemat</div>
                <h4>Tahunan</h4>
                <div class="desc">Satu tahun penuh, semua produk</div>
                <div class="amt">{ui.rupiah(PRICE_YEAR)}</div>
                <div class="per">per tahun</div>
                <div class="was">{ui.rupiah(PRICE_YEAR_WAS)}</div>
                <ul>
                    <li>Semua keuntungan paket bulanan</li>
                    <li>Antrean proses diprioritaskan</li>
                    <li>Batas unggahan lebih besar</li>
                    <li>Produk baru langsung terbuka</li>
                    <li>Dukungan lewat WhatsApp</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    with c3:
        st.markdown(
            f"""
            <div class="amp-price">
                <h4>Sekali bayar</h4>
                <div class="desc">Bayar sekali, pakai selamanya</div>
                <div class="amt">{ui.rupiah(PRICE_LIFETIME)}</div>
                <div class="per">sekali bayar</div>
                <ul>
                    <li>Semua keuntungan paket tahunan</li>
                    <li>Tanpa perpanjangan</li>
                    <li>Nama tercantum sebagai pendukung awal</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    st.write("")
    b1, b2, b3 = st.columns([1, 2, 1])
    with b2:
        if st.button("Gabung sekarang", type="primary", width="stretch",
                     key="join_cta"):
            st.success(
                "Terima kasih! Pendaftaran belum dibuka — tinggalkan surelmu di "
                "bawah, kami kabari begitu kuotanya siap.")
        email = st.text_input("Surel", placeholder="nama@surel.com",
                              label_visibility="collapsed", key="join_email")
        if email:
            st.caption("Tercatat. Kami hubungi lewat surel ini.")

    st.caption("Harga masih bersifat sementara dan dapat berubah sebelum peluncuran.")

    ui.footer("© Ampera Upscale — 2026")
