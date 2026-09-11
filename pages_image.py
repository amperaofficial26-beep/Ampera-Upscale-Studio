"""Halaman 2 — Image Upscale: unggah, pratinjau kecil, identitas + kualitas, model."""

import os
import time

import streamlit as st

import analysis as A
import enhance as E
import presets as P
import ui


def render():
    ui.brand("Image Upscale", "Foto",
             "Unggah foto, periksa identitas dan kualitasnya, lalu pilih model.")

    ui.label("1 · Unggah gambar")
    up = st.file_uploader("Gambar", type=["png", "jpg", "jpeg", "webp", "bmp"],
                          label_visibility="collapsed", key="img_up")
    st.caption(f"JPG, PNG, WebP atau BMP · maksimal {ui.human_size(E.MAX_PHOTO_BYTES)}")

    if not up:
        st.write("")
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

    # ---------------------------------------------- pratinjau kecil + identitas
    ui.label("2 · Identitas gambar")
    prev, ident = st.columns([1, 1.55])
    with prev:
        st.image(img, channels="BGR", width=300)
        st.caption("Pratinjau")
    with ident:
        rows = A.image_identity(img, up.name, up.size)
        rows.insert(2, ("Ukuran berkas", ui.human_size(up.size)))
        ui.identity_table(rows)

    # ---------------------------------------------- kualitas
    st.write("")
    ui.label("Penilaian kualitas")
    q = A.quality_verdict(img, up.size)
    ui.quality_chips(q["metrics"])
    st.write("")
    ui.score_box(q["score"], q["verdict"])

    # ---------------------------------------------- model
    ui.label("3 · Pilihan model")
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
    ui.label("4 · Proses")
    if model_key:
        est = (f"± {ui.human_time(E.estimate_seconds(w, h, model_key))} · "
               f"{E.estimate_tiles(w, h, model_key)} tile")
    else:
        est = "beberapa detik"

    ready = (P.ensure_model(model_key) if model_key else
             P.ensure_model(scale) if engine == "fsrcnn" else True)

    rows = [("Hasil", f"{w * scale} × {h * scale}"),
            ("Kelas resolusi", A.resolution_class(w * scale, h * scale)),
            ("Perkiraan waktu", est)]
    if model_key and E.TILE_WORKERS > 1:
        rows.append(("Proses paralel", f"{E.TILE_WORKERS} tile sekaligus"))
    ui.stats(rows)
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
            st.session_state.img_result = {
                "data": result, "elapsed": time.time() - t0,
                "name": os.path.splitext(up.name)[0],
                "src_w": w, "src_h": h,
            }

    # ---------------------------------------------- hasil
    res = st.session_state.get("img_result")
    if res is not None and res["src_w"] == w and res["src_h"] == h:
        out = res["data"]
        png = E.encode_image(out, ".png")
        jpg = E.encode_image(out, ".jpg")

        st.divider()
        ui.label("Hasil")
        ui.stats([
            ("Resolusi", f"{w} × {h}  →  {out.shape[1]} × {out.shape[0]}"),
            ("Waktu", ui.human_time(res["elapsed"])),
            ("Ketajaman", f"{A.sharpness_score(img):.0f} → {A.sharpness_score(out):.0f}"),
            ("Ukuran PNG", ui.human_size(len(png))),
        ])
        st.write("")
        c1, c2 = st.columns(2)
        with c1:
            st.image(img, channels="BGR", width="stretch")
            st.caption("Sebelum")
        with c2:
            st.image(out, channels="BGR", width="stretch")
            st.caption("Sesudah")

        d1, d2 = st.columns(2)
        d1.download_button("Unduh PNG", png, f"{res['name']}_upscaled.png",
                           "image/png", width="stretch")
        d2.download_button("Unduh JPG", jpg, f"{res['name']}_upscaled.jpg",
                           "image/jpeg", width="stretch")

    ui.footer("© Ampera Upscale — 2026")
