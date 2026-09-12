"""Halaman 2 — Foto: unggah, pratinjau, identitas + kualitas, model, proses."""

import os
import time

import streamlit as st

import analysis as A
import enhance as E
import presets as P
import ui


def render():
    ui.brand("Foto", "Peningkatan kualitas",
             "Unggah foto, lihat analisisnya, lalu pilih model yang paling cocok.")

    # ---------------------------------------------- unggah
    ui.label("Unggah foto")
    up = st.file_uploader("Gambar", type=["png", "jpg", "jpeg", "webp", "bmp"],
                          label_visibility="collapsed", key="img_up")
    st.caption(f"JPG, PNG, WebP atau BMP · maksimal {ui.human_size(E.MAX_PHOTO_BYTES)}")

    if not up:
        ui.note("Belum ada gambar. Unggah satu berkas untuk melihat analisis lengkapnya.")
        ui.footer("© Ampera Upscale — 2026")
        return

    if up.size > E.MAX_PHOTO_BYTES:
        st.error(f"Gambar {ui.human_size(up.size)} melebihi batas "
                 f"{ui.human_size(E.MAX_PHOTO_BYTES)}. Kompres dulu, lalu unggah ulang.")
        ui.footer("© Ampera Upscale — 2026")
        return

    try:
        img = E.decode_image(up.getvalue())
    except Exception as ex:
        st.error(f"Gagal membaca gambar: {ex}")
        ui.footer("© Ampera Upscale — 2026")
        return

    h, w = img.shape[:2]

    # ---------------------------------------------- analisis
    ui.label("Analisis")
    prev, ident = st.columns([1, 1.55])
    with prev:
        st.image(img, channels="BGR", width=300)
        st.caption("Pratinjau")
    with ident:
        rows = A.image_identity(img, up.name, up.size)
        rows.insert(2, ("Ukuran berkas", ui.human_size(up.size)))
        ui.identity_table(rows)

    st.write("")
    q = A.quality_verdict(img, up.size)
    ui.quality_chips(q["metrics"])
    st.write("")
    ui.score_box(q["score"], q["verdict"])

    # ---------------------------------------------- model
    ui.label("Pilihan model")
    engine, model_key, scale = P.preset_picker(P.PHOTO_PRESETS, "img_preset")

    with st.expander("Pengaturan lanjutan"):
        if engine in ("fsrcnn", "classic"):
            opts = [2, 3, 4] if engine == "fsrcnn" else [2, 4]
            scale = st.select_slider("Pembesaran", opts, value=2,
                                     format_func=lambda s: f"{s}×", key="img_scale")
        else:
            st.caption(f"Model ini memakai pembesaran tetap {scale}×.")
        sharpen = st.slider("Ketajaman tambahan", 0, 100, 30, 5, key="img_sharp",
                            help="Unsharp mask setelah pembesaran. 0 menonaktifkan.")

    # ---------------------------------------------- proses
    ui.label("Proses")
    ew, eh = E.budget_dims(w, h, scale, engine)   # dimensi efektif setelah anggaran
    if model_key:
        est = (f"± {ui.human_time(E.estimate_seconds(ew, eh, model_key))} · "
               f"{E.estimate_tiles(ew, eh, model_key)} tile")
    else:
        est = "beberapa detik"

    ready = (P.ensure_model(model_key) if model_key else
             P.ensure_model(scale) if engine == "fsrcnn" else True)

    ui.stats([("Hasil", f"{ew * scale} × {eh * scale}"),
              ("Kelas resolusi", A.resolution_class(ew * scale, eh * scale)),
              ("Perkiraan waktu", est)])
    if (ew, eh) != (w, h):
        st.write("")
        ui.note(f"Foto {w} × {h} piksel terlalu besar untuk diproses penuh di "
                f"memori server. Kami perkecil ke {ew} × {eh} dulu — hasil "
                f"akhir tetap jauh lebih besar dan lebih tajam dari aslinya.")
    st.write("")

    if st.button("Tingkatkan kualitas gambar", type="primary",
                 disabled=not ready, width="stretch", key="img_go"):
        t0 = time.time()
        bar = st.progress(0.0, text="Memuat model…")
        try:
            result = E.enhance_image(
                img, engine, model_key, scale, sharpen=sharpen / 100.0,
                progress_cb=(lambda i, n: bar.progress(
                    min(i / n, 1.0), text=f"Tile {i} dari {n}")) if model_key else None)
        except Exception as ex:
            bar.empty()
            st.error(f"Gagal memproses: {ex}")
            result = None
        else:
            bar.empty()

        if result is not None:
            # simpan sebagai bytes (PNG/JPG), bukan array — hemat RAM sesi
            png = E.encode_image(result, ".png")
            jpg = E.encode_image(result, ".jpg")
            st.session_state.img_result = {
                "png": png, "jpg": jpg,
                "elapsed": time.time() - t0,
                "name": os.path.splitext(up.name)[0],
                "token": (up.name, up.size),
                "out_w": result.shape[1], "out_h": result.shape[0],
                "sharp_before": A.sharpness_score(img),
                "sharp_after": A.sharpness_score(result),
            }

    # ---------------------------------------------- hasil
    res = st.session_state.get("img_result")
    if res is not None and res.get("token") == (up.name, up.size):
        st.divider()
        ui.label("Hasil")
        ui.stats([
            ("Resolusi", f"{w} × {h}  →  {res['out_w']} × {res['out_h']}"),
            ("Waktu", ui.human_time(res["elapsed"])),
            ("Ketajaman", f"{res['sharp_before']:.0f} → {res['sharp_after']:.0f}"),
            ("Ukuran PNG", ui.human_size(len(res["png"]))),
        ])
        st.write("")
        c1, c2 = st.columns(2)
        with c1:
            st.image(img, channels="BGR", width="stretch")
            st.caption("Sebelum")
        with c2:
            st.image(res["png"], width="stretch")
            st.caption("Sesudah")

        d1, d2 = st.columns(2)
        d1.download_button("Unduh PNG", res["png"], f"{res['name']}_upscaled.png",
                           "image/png", width="stretch")
        d2.download_button("Unduh JPG", res["jpg"], f"{res['name']}_upscaled.jpg",
                           "image/jpeg", width="stretch")

    ui.footer("© Ampera Upscale — 2026")
