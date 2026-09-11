"""Halaman 5 — Pelajari Lebih Lanjut: cara kerja, model, batasan, tanya jawab."""

import streamlit as st

import enhance as E
import ui


def render():
    ui.brand("Pelajari Lebih Lanjut", "Panduan",
             "Bagaimana Ampera Upscale bekerja, dan model mana yang sebaiknya dipakai.")

    # ---------------------------------------------- cara kerja
    ui.label("Cara kerja singkat")
    st.markdown(
        """
        <div class="amp-card">
        <p style="margin:0; color:#B4BCC7; font-size:.92rem; line-height:1.75;">
        Gambarmu dipecah menjadi ubin kecil berukuran 256 piksel, lalu tiap ubin
        dilewatkan ke jaringan saraf yang sudah dilatih mengenali bagaimana
        tekstur asli seharusnya terlihat. Hasilnya disatukan kembali dengan
        teknik <i>cross-fade</i> sehingga tidak ada garis sambungan.
        Pendekatan per-ubin ini membuat aplikasi tetap ringan — foto besar
        sekalipun bisa diproses di mesin dengan RAM 2 GB.
        </p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    s1, s2, s3 = st.columns(3)
    steps = [
        ("1 · Pecah", "Gambar dibagi jadi ubin 256 px dengan tepi bertumpang tindih."),
        ("2 · Tingkatkan", "Tiap ubin diperbesar model AI, detail direkonstruksi."),
        ("3 · Satukan", "Ubin digabung dengan cross-fade, lalu dipertajam."),
    ]
    for col, (t, d) in zip((s1, s2, s3), steps):
        with col:
            st.markdown(f'<div class="amp-feat"><div class="t">{t}</div>'
                        f'<div class="d">{d}</div></div>', unsafe_allow_html=True)

    # ---------------------------------------------- model
    st.write("")
    ui.label("Model yang tersedia")
    models = [
        ("Real-ESRGAN 6B", "realesrgan_anime", "Foto & ilustrasi",
         "Paling detail. Cocok saat hasil akhir yang diutamakan, bukan kecepatan."),
        ("Real-ESRGAN AnimeVideoV3", "realesrgan_animevid", "Serba guna",
         "Nyaris secepat kilat dengan hasil tetap tajam. Pilihan utama untuk video."),
        ("Real-CUGAN", "cugan_x4", "Anime & 2D",
         "Menjaga garis tetap bersih dan warna tetap rata pada gambar kartun."),
        ("FSRCNN", None, "Instan",
         "Sangat ringan, hasilnya lebih halus daripada pembesaran biasa."),
        ("Lanczos klasik", None, "Tanpa AI",
         "Pembesaran matematis murni. Selalu tersedia, tanpa perlu model."),
    ]
    for name, key, tag, desc in models:
        if key:
            size = ui.human_size(E.MODEL_DOWNLOADS[E.SPANDREL_MODELS[key][0]][1])
            status = ("Siap dipakai" if E.model_missing(key) is None
                      else "Perlu diunduh")
            meta = f"{tag} · {size} · {status}"
        else:
            meta = f"{tag} · tanpa bobot tambahan"
        st.markdown(
            f"""
            <div class="amp-idt" style="margin-bottom:.5rem;">
              <div class="row" style="flex-direction:column; align-items:flex-start; gap:.3rem;">
                <div style="display:flex; justify-content:space-between; width:100%; gap:1rem;">
                  <span class="v" style="text-align:left; font-size:.95rem;">{name}</span>
                  <span class="k" style="white-space:nowrap;">{meta}</span>
                </div>
                <span class="k" style="font-size:.84rem; line-height:1.5;">{desc}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

    # ---------------------------------------------- batasan
    st.write("")
    ui.label("Batas dan alasannya")
    ui.stats([("Foto", ui.human_size(E.MAX_PHOTO_BYTES)),
              ("Video", f"{E.MAX_VIDEO_SECONDS} detik"),
              ("Ukuran ubin", f"{E.DEFAULT_TILE} px"),
              ("Model tersimpan", f"maks {E.MAX_CACHE}")])
    st.write("")
    ui.note(
        "Batas ini menjaga aplikasi tetap responsif di server bersama. Video "
        "diproses satu frame sekaligus, jadi klip 10 detik berarti ratusan kali "
        "kerja dibanding satu foto — karena itu durasinya dibatasi."
    )

    # ---------------------------------------------- tanya jawab
    st.write("")
    ui.label("Tanya jawab")
    faqs = [
        ("Apakah berkas saya disimpan?",
         "Tidak. Berkas hanya ada di memori sementara server selama proses "
         "berlangsung, lalu dibuang. Tidak ada yang dikirim ke layanan luar."),
        ("Kenapa prosesnya terasa lama?",
         "Aplikasi ini berjalan di CPU, bukan kartu grafis. Perkiraan waktu yang "
         "kami tampilkan sebelum proses dihitung dari kecepatan CPU sebenarnya, "
         "jadi angkanya cukup jujur. Pakai model Seimbang atau Cepat bila terburu-buru."),
        ("Bisakah gambar sangat buram dipulihkan sempurna?",
         "Tidak sepenuhnya. Model merekonstruksi detail yang masuk akal, bukan "
         "mengembalikan informasi yang benar-benar sudah hilang. Makin baik "
         "sumbernya, makin meyakinkan hasilnya."),
        ("Kenapa hasil video ukurannya membengkak?",
         "Resolusi naik dua sampai empat kali lipat, jadi jumlah pikselnya "
         "berlipat. Kami sudah memakai H.264 dengan mutu tinggi agar seimbang "
         "antara ukuran dan ketajaman."),
        ("Model mana yang harus saya pilih?",
         "Untuk foto kenangan, pakai Kualitas terbaik. Untuk video atau saat "
         "sedang buru-buru, pakai Seimbang. Untuk gambar anime dan ilustrasi, "
         "pakai Anime & ilustrasi."),
    ]
    for q, a in faqs:
        with st.expander(q):
            st.markdown(
                f'<span style="color:#B4BCC7; font-size:.9rem; line-height:1.7;">{a}</span>',
                unsafe_allow_html=True)

    ui.footer("© Ampera Upscale — 2026")
