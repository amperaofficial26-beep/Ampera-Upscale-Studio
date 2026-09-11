"""
Ampera Enhance — UI Streamlit.

Desain: elegan & sederhana. Alur dibuat linear (Unggah → Kualitas → Proses)
dan opsi teknis disembunyikan di bagian "Pengaturan lanjutan".
"""

import os
import tempfile
import time

import streamlit as st

import enhance as E
import ui

st.set_page_config(
    page_title="Ampera Enhance",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="collapsed",
)
ui.inject_css()

# ---------------------------------------------------------------- preset
# Satu preset = satu baris pilihan di UI. Detail model disembunyikan.
#   key: (judul, keterangan, engine, model_key, scale bawaan)
PHOTO_PRESETS = {
    "quality":  ("Kualitas terbaik", "Real-ESRGAN 6B · paling detail, paling lambat",
                 "ai", "realesrgan_anime", 4),
    "balanced": ("Seimbang", "Real-ESRGAN AnimeVideoV3 · tajam dan jauh lebih cepat",
                 "ai", "realesrgan_animevid", 4),
    "anime":    ("Anime & ilustrasi", "Real-CUGAN · garis bersih untuk gambar 2D",
                 "ai", "cugan_x4", 4),
    "fast":     ("Cepat", "FSRCNN · hasil instan, detail seadanya",
                 "fsrcnn", None, 2),
    "classic":  ("Tanpa AI", "Lanczos + unsharp · pembesaran klasik",
                 "classic", None, 2),
}
VIDEO_PRESETS = {
    "balanced": ("Seimbang", "Real-ESRGAN AnimeVideoV3 · pilihan terbaik untuk video",
                 "ai", "realesrgan_animevid", 4),
    "quality":  ("Kualitas terbaik", "Real-ESRGAN 6B · sangat lambat di CPU",
                 "ai", "realesrgan_anime", 4),
    "anime":    ("Anime & ilustrasi", "Real-CUGAN · garis bersih untuk gambar 2D",
                 "ai", "cugan_x4", 4),
    "fast":     ("Cepat", "FSRCNN · hasil instan, detail seadanya",
                 "fsrcnn", None, 2),
}


def _preset_available(preset: tuple) -> bool:
    """True bila bobot model preset ini sudah ada di server."""
    _, _, engine, model_key, scale = preset
    if model_key:
        return E.model_missing(model_key) is None
    if engine == "fsrcnn":
        return E.model_missing(scale) is None
    return True


def preset_picker(presets: dict, key: str) -> tuple:
    """Tampilkan daftar preset. Return (engine, model_key, scale bawaan)."""
    keys = list(presets)
    avail = {k: _preset_available(presets[k]) for k in keys}

    def fmt(k):
        title, desc, *_ = presets[k]
        suffix = "" if avail[k] else " · perlu unduh model"
        return f"**{title}** — {desc}{suffix}"

    # default ke preset pertama yang bobotnya sudah tersedia
    default = next((i for i, k in enumerate(keys) if avail[k]), 0)
    choice = st.radio("Preset", keys, index=default, format_func=fmt,
                      label_visibility="collapsed", key=key)
    _, _, engine, model_key, scale = presets[choice]
    return engine, model_key, scale


def ensure_model(model_key) -> bool:
    """True bila bobot model tersedia. Bila tidak, tampilkan tombol unduh."""
    missing = E.model_missing(model_key)
    if missing is None:
        return True

    size = E.MODEL_DOWNLOADS[missing][1]
    ui.note(
        f"Bobot model <b>{missing}</b> ({ui.human_size(size)}) belum ada di server ini. "
        "Unduh sekali saja — setelah itu tersimpan permanen.")
    if st.button(f"Unduh model · {ui.human_size(size)}", key=f"dl_{missing}"):
        bar = st.progress(0.0, text="Mengunduh…")
        try:
            E.download_model(
                missing,
                progress_cb=lambda d, t: bar.progress(
                    min(d / t, 1.0) if t else 0.0,
                    text=f"{ui.human_size(d)} / {ui.human_size(t)}"))
            bar.empty()
            st.rerun()
        except Exception as ex:
            bar.empty()
            st.error(f"Gagal mengunduh model: {ex}")
    return False


# ---------------------------------------------------------------- header
ui.brand("Ampera Enhance", "Ampera Official",
         "Perbesar dan pertajam foto atau video dengan model AI ringan.")

tab_photo, tab_video = st.tabs(["Foto", "Video"])

# ================================================================ FOTO
with tab_photo:
    ui.label("1 · Unggah foto")
    up = st.file_uploader(
        "Foto", type=["png", "jpg", "jpeg", "webp", "bmp"],
        label_visibility="collapsed", key="photo_up")
    st.caption(f"JPG, PNG, WebP atau BMP · maksimal {ui.human_size(E.MAX_PHOTO_BYTES)}")

    if up and up.size > E.MAX_PHOTO_BYTES:
        st.error(
            f"Foto {ui.human_size(up.size)} melebihi batas "
            f"{ui.human_size(E.MAX_PHOTO_BYTES)}. Kompres dulu, lalu unggah ulang.")

    elif up:
        try:
            img = E.decode_image(up.getvalue())
        except Exception as ex:
            st.error(f"Gagal membaca gambar: {ex}")
            img = None

        if img is not None:
            h, w = img.shape[:2]
            ui.stats([("Resolusi", f"{w} × {h}"),
                      ("Ukuran", ui.human_size(up.size)),
                      ("Format", os.path.splitext(up.name)[1].lstrip(".").upper() or "—")])
            st.write("")
            st.image(img, channels="BGR", width="stretch")

            ui.label("2 · Pilih kualitas")
            engine, model_key, scale = preset_picker(PHOTO_PRESETS, "photo_preset")

            with st.expander("Pengaturan lanjutan"):
                if engine in ("fsrcnn", "classic"):
                    opts = [2, 3, 4] if engine == "fsrcnn" else [2, 4]
                    scale = st.select_slider(
                        "Pembesaran", opts, value=2,
                        format_func=lambda s: f"{s}×", key="photo_scale")
                else:
                    st.caption(f"Preset ini memakai pembesaran tetap {scale}×.")
                sharpen = st.slider(
                    "Ketajaman tambahan", 0, 100, 30, 5, key="photo_sharp",
                    help="Unsharp mask setelah pembesaran. 0 menonaktifkan.")

            ui.label("3 · Proses")
            if model_key:
                secs = E.estimate_seconds(w, h, model_key)
                tiles = E.estimate_tiles(w, h, model_key)
                est = f"± {ui.human_time(secs)} · {tiles} tile"
            else:
                est = "beberapa detik"

            ready = ensure_model(model_key) if model_key else (
                ensure_model(scale) if engine == "fsrcnn" else True)

            ui.stats([("Hasil", f"{w * scale} × {h * scale}"),
                      ("Perkiraan waktu", est)])
            st.write("")

            go = st.button("Proses foto", type="primary", disabled=not ready,
                           width="stretch", key="photo_go")

            if go:
                t0 = time.time()
                bar = st.progress(0.0, text="Memuat model…")
                try:
                    result = E.enhance_image(
                        img, engine, model_key, scale, sharpen=sharpen / 100.0,
                        progress_cb=(lambda i, n: bar.progress(
                            min(i / n, 1.0), text=f"Tile {i} dari {n}"))
                        if model_key else None)
                except Exception as ex:
                    bar.empty()
                    st.error(f"Gagal memproses: {ex}")
                    result = None
                else:
                    bar.empty()

                if result is not None:
                    elapsed = time.time() - t0
                    png = E.encode_image(result, ".png")
                    jpg = E.encode_image(result, ".jpg")

                    st.divider()
                    ui.label("Hasil")
                    ui.stats([
                        ("Resolusi", f"{w} × {h}  →  {result.shape[1]} × {result.shape[0]}"),
                        ("Waktu", ui.human_time(elapsed)),
                        ("Ukuran PNG", ui.human_size(len(png))),
                    ])
                    st.write("")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.image(img, channels="BGR", width="stretch")
                        st.caption("Sebelum")
                    with c2:
                        st.image(result, channels="BGR", width="stretch")
                        st.caption("Sesudah")

                    stem = os.path.splitext(up.name)[0]
                    d1, d2 = st.columns(2)
                    d1.download_button("Unduh PNG", png, f"{stem}_enhanced.png",
                                       "image/png", width="stretch")
                    d2.download_button("Unduh JPG", jpg, f"{stem}_enhanced.jpg",
                                       "image/jpeg", width="stretch")
    else:
        st.write("")
        ui.note(
            "Semua proses berjalan di server ini — foto tidak dikirim ke layanan pihak ketiga.")

# ================================================================ VIDEO
with tab_video:
    ui.label("1 · Unggah video")
    vup = st.file_uploader(
        "Video", type=["mp4", "webm", "mov", "avi", "mkv"],
        label_visibility="collapsed", key="video_up")
    st.caption(f"MP4, WebM, MOV, AVI atau MKV · maksimal {E.MAX_VIDEO_SECONDS} detik · "
               "audio asli dipertahankan")

    if vup:
        vtmp = os.path.join(tempfile.gettempdir(), "ampera_in_" + vup.name)
        with open(vtmp, "wb") as f:
            f.write(vup.getvalue())

        info = E.video_info(vtmp)
        if not info or not info.get("frames"):
            st.error("Video tidak dapat dibaca. Coba format lain, misalnya MP4 (H.264).")
        else:
            ui.stats([("Durasi", f"{info['duration']:.1f} dtk".replace(".", ",")),
                      ("Resolusi", f"{info['w']} × {info['h']}"),
                      ("FPS", f"{info['fps']:.0f}"),
                      ("Frame", f"{info['frames']}")])

            if info["duration"] > E.MAX_VIDEO_SECONDS + 0.25:
                st.write("")
                st.error(
                    f"Durasi {info['duration']:.1f} detik melebihi batas "
                    f"{E.MAX_VIDEO_SECONDS} detik. Potong videonya lalu unggah ulang.")
            else:
                st.write("")
                st.video(vtmp)

                ui.label("2 · Pilih kualitas")
                engine, model_key, scale = preset_picker(VIDEO_PRESETS, "video_preset")

                frame_cap = max(int(info["fps"] * E.MAX_VIDEO_SECONDS), 1)
                with st.expander("Pengaturan lanjutan"):
                    if engine == "fsrcnn":
                        scale = st.select_slider(
                            "Pembesaran", [2, 3, 4], value=2,
                            format_func=lambda s: f"{s}×", key="video_scale")
                    else:
                        st.caption(f"Preset ini memakai pembesaran tetap {scale}×.")
                    max_frames = st.number_input(
                        "Batas frame (0 = semua)", 0, frame_cap, 0, step=10,
                        key="video_maxf",
                        help="Isi angka kecil untuk uji coba cepat sebelum proses penuh.")
                    sharpen = st.slider("Ketajaman tambahan", 0, 100, 0, 5,
                                        key="video_sharp")

                ui.label("3 · Proses")
                n_proc = (info["frames"] if max_frames <= 0
                          else min(int(max_frames), info["frames"]))
                if model_key:
                    tiles = E.estimate_tiles(info["w"], info["h"], model_key)
                    est = ui.human_time(n_proc * tiles * E.TILE_SECONDS[model_key])
                else:
                    est = ui.human_time(n_proc * 0.4)

                ready = ensure_model(model_key) if model_key else ensure_model(scale)

                ui.stats([("Hasil", f"{info['w'] * scale} × {info['h'] * scale}"),
                          ("Frame diproses", f"{n_proc}"),
                          ("Perkiraan waktu", f"± {est}")])
                st.write("")

                go = st.button("Proses video", type="primary", disabled=not ready,
                               width="stretch", key="video_go")

                if go:
                    out_path = os.path.join(
                        tempfile.gettempdir(), f"ampera_out_{int(time.time())}.mp4")
                    bar = st.progress(0.0, text="Menyiapkan…")

                    def _cb(i, total, elapsed):
                        eta = elapsed / max(i, 1) * (total - i)
                        bar.progress(min(i / total, 1.0),
                                     text=f"Frame {i} dari {total} · sisa ± {ui.human_time(eta)}")

                    try:
                        res = E.process_video(
                            vtmp, out_path, engine, model_key, scale,
                            max_frames=int(max_frames), sharpen=sharpen / 100.0,
                            keep_audio=True, progress_cb=_cb)
                    except Exception as ex:
                        bar.empty()
                        st.error(f"Gagal memproses video: {ex}")
                        res = None
                    else:
                        bar.empty()

                    if res:
                        with open(out_path, "rb") as f:
                            data = f.read()

                        st.divider()
                        ui.label("Hasil")
                        ui.stats([
                            ("Resolusi",
                             f"{res['in_w']} × {res['in_h']}  →  {res['out_w']} × {res['out_h']}"),
                            ("Frame", f"{res['frames']}"),
                            ("Waktu", ui.human_time(res["elapsed"])),
                            ("Audio", "dipertahankan" if res["audio"] else "tidak ada"),
                            ("Ukuran", ui.human_size(len(data))),
                        ])
                        st.write("")
                        st.video(out_path)
                        st.caption("Hasil peningkatan")
                        st.download_button(
                            "Unduh video", data,
                            f"{os.path.splitext(vup.name)[0]}_enhanced.mp4",
                            "video/mp4", width="stretch")
    else:
        st.write("")
        ui.note(
            "Video diproses frame demi frame di CPU. Untuk hasil tercepat gunakan preset "
            "<b>Seimbang</b> dan durasi sesingkat mungkin.")
