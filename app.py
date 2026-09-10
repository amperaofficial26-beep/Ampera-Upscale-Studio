import os
import tempfile
import time

import streamlit as st

import enhance as E
import supir

st.set_page_config(
    page_title="Ampera Enhance",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("✨ Ampera Enhance")
st.caption(
    "Foto & video, naik kelas — by **Ampera Official**.  "
    "Batas: **foto maksimal 20 MB** • **video maksimal 10 detik**."
)

tab_photo, tab_video = st.tabs(["📷 Foto", "🎬 Video"])

# ---------------------------------------------------------------- engine
PHOTO_ENGINES = [
    ("realesrgan", "🥇 Real-ESRGAN — Utama"),
    ("swinir",     "🥈 SwinIR — Natural"),
    ("cugan",      "🥉 Real-CUGAN — Anime"),
    ("hat",        "🔥 HAT — Ultra Quality"),
    ("supir",      "💎 SUPIR — Eksperimental (kualitas maksimal)"),
    ("fsrcnn",     "⚡ FSRCNN — Cepat (ringan)"),
    ("classic",    "🔧 Klasik — Lanczos (tanpa AI)"),
]
VIDEO_ENGINES = [
    ("fsrcnn",     "⚡ FSRCNN — Cepat (disarankan untuk CPU)"),
    ("realesrgan", "🥇 Real-ESRGAN — Utama"),
    ("swinir",     "🥈 SwinIR — Natural"),
    ("cugan",      "🥉 Real-CUGAN — Anime"),
    ("hat",        "🔥 HAT — Ultra Quality"),
]

def _ensure_model_ready(model_key) -> bool:
    """Jika file model belum ada di server, tampilkan tombol unduh. Return True jika siap."""
    missing = E.model_missing(model_key)
    if missing is None:
        return True
    url, size = E.MODEL_DOWNLOADS[missing]
    st.warning(
        f"Model **{missing}** belum ada di server ini ({size / 1024 / 1024:.0f} MB). "
        "Unduh dulu, atau jalankan `python download_models.py` di terminal.")
    if st.button(f"⬇️ Unduh model ({size / 1024 / 1024:.0f} MB)", key=f"dl_{missing}"):
        pbar = st.progress(0.0, text="Mengunduh…")
        try:
            def _cb(done, tot):
                if tot:
                    pbar.progress(done / tot,
                                  text=f"⬇️ {done / 1024 / 1024:.1f} / {tot / 1024 / 1024:.1f} MB")
            E.download_model(missing, progress_cb=_cb)
            pbar.progress(1.0, text="Selesai ✅")
            st.success(f"Model {missing} terunduh — silakan proses ulang.")
            st.rerun()
        except Exception as ex:
            pbar.empty()
            st.error(f"Gagal mengunduh model: {ex}")
    return False


# ---------------------------------------------------------------- Foto
with tab_photo:
    st.header("📷 Foto  (maks 20 MB)")
    up = st.file_uploader(
        "Unggah foto (JPG / PNG / WebP)", type=["png", "jpg", "jpeg", "webp", "bmp"],
        key="photo_up")

    if up and up.size > E.MAX_PHOTO_BYTES:
        st.error(f"⛔ Foto terlalu besar: {up.size / 1024 / 1024:.1f} MB. "
                 f"Maksimal **20 MB**. Silakan kompres dulu.")
        st.stop()

    if up:
        img = E.decode_image(up.getvalue())
        st.image(img, channels="BGR",
                 caption=f"Original — {img.shape[1]}×{img.shape[0]}  •  {up.size/1024/1024:.1f} MB",
                 use_container_width=True)

        engine = st.radio(
            "Model / Engine",
            [e for e, _ in PHOTO_ENGINES],
            horizontal=False,
            format_func=lambda e: dict(PHOTO_ENGINES)[e],
            key="photo_engine",
        )

        model_key = None
        scale = 2
        c1, c2, c3 = st.columns([2, 1.4, 1.4])
        with c1:
            if engine == "realesrgan":
                model_key = st.selectbox(
                    "Model Real-ESRGAN",
                    ["realesrgan_x4plus", "realesrgan_anime", "realesrgan_x2plus"],
                    format_func=lambda k: f"{k.replace('realesrgan_', '').upper()} — {E.SPANDREL_MODELS[k][2]}",
                    key="photo_rm")
                scale = E.SPANDREL_MODELS[model_key][1]
            elif engine in ("swinir", "cugan", "hat"):
                model_key = engine + "_x4"
                scale = 4
                st.caption({"swinir": "🥈 Hasil natural, detail halus",
                            "cugan": "🥉 Dioptimalkan untuk anime / ilustrasi",
                            "hat": "🔥 Ultra quality (transformer hybrid, terlama)"}[engine])
            elif engine == "fsrcnn":
                scale = st.selectbox("Pembesaran", [2, 3, 4],
                                     format_func=lambda s: f"{s}x", key="photo_fs_scale")
            elif engine == "classic":
                scale = st.selectbox("Pembesaran", [2, 4],
                                     format_func=lambda s: f"{s}x", key="photo_cl_scale")
        with c2:
            sharpen = st.slider("Sharpening tambahan", 0, 100, 30, 5,
                                help="Unsharp mask. 0 = nonaktif.", key="photo_sharp")
        with c3:
            if engine == "supir":
                supir_upscale = st.selectbox("Upscale", [1, 2, 4],
                                             format_func=lambda s: f"{s}x (min 1024 px)",
                                             key="supir_us")
                supir_steps = st.slider("Diffusion steps", 10, 100, 50, 5, key="supir_steps")

        supir_ready, supir_msg = (None, None)
        if engine == "supir":
            supir_ready, supir_msg = supir.supir_status()
            if not supir_ready:
                st.warning("💎 " + supir_msg)
            else:
                st.success("💎 " + supir_msg)

        out_w, out_h = img.shape[1] * scale, img.shape[0] * scale
        if engine == "supir":
            est_text = "SUPIR: proses diffusion (puluhan detik–menit, butuh GPU)"
        elif model_key:
            nt = E.estimate_tiles(img.shape[1], img.shape[0], model_key)
            est_text = (f"Estimasi CPU: ±{nt} tile × {E.TILE_SECONDS[model_key]} dtk "
                        f"≈ **{E.estimate_seconds(img.shape[1], img.shape[0], model_key) / 60:.0f} menit**")
        else:
            est_text = "Cepat (≤ beberapa detik)"

        model_ready = True
        if model_key:
            model_ready = _ensure_model_ready(model_key)
        elif engine == "fsrcnn":
            model_ready = _ensure_model_ready(scale)

        b1, b2 = st.columns([1, 3])
        with b1:
            can_run = (engine != "supir" or supir_ready) and model_ready
            go = st.button("🚀 Proses", type="primary", use_container_width=True,
                           disabled=not can_run, key="photo_go")
        with b2:
            st.caption(f"Hasil: {out_w}×{out_h} px — {est_text}")

        if go and can_run:
            t0 = time.time()
            pbar = st.progress(0.0, text="Memuat model…")

            def _cb(i, total):
                pbar.progress(min(i / total, 1.0), text=f"Mengolah tile {i}/{total}…")

            try:
                if engine == "supir":
                    st.spinner("SUPIR memuat model & menjalankan diffusion…")
                    result = supir.enhance_supir(img, upscale=supir_upscale,
                                                 steps=supir_steps)
                else:
                    result = E.enhance_image(
                        img, "ai" if model_key else engine, model_key, scale,
                        sharpen=sharpen / 100.0,
                        progress_cb=_cb if model_key else None)
                pbar.progress(1.0, text="Selesai ✅")
            except Exception as ex:
                pbar.empty()
                st.error(f"Gagal memproses: {ex}")
                st.stop()

            st.success(f"Selesai dalam {time.time() - t0:.1f} detik.")
            c1, c2 = st.columns(2)
            with c1:
                st.image(img, channels="BGR",
                         caption=f"Sebelum — {img.shape[1]}×{img.shape[0]}",
                         use_container_width=True)
            with c2:
                st.image(result, channels="BGR",
                         caption=f"Sesudah — {result.shape[1]}×{result.shape[0]}",
                         use_container_width=True)

            png = E.encode_image(result, ".png")
            jpg = E.encode_image(result, ".jpg")
            d1, d2, _ = st.columns(3)
            d1.download_button("⬇️ Unduh PNG", png,
                               f"{up.name}_enhanced.png", "image/png",
                               use_container_width=True)
            d2.download_button("⬇️ Unduh JPG", jpg,
                               f"{up.name}_enhanced.jpg", "image/jpeg",
                               use_container_width=True)
            m1, m2, m3 = st.columns(3)
            m1.metric("Resolusi", f"{img.shape[1]}×{img.shape[0]} → {result.shape[1]}×{result.shape[0]}")
            m2.metric("Waktu", f"{time.time() - t0:.1f} dtk")
            m3.metric("Ukuran hasil", f"{len(png) / 1024 / 1024:.1f} MB (PNG)")

# ---------------------------------------------------------------- Video
with tab_video:
    st.header("🎬 Video  (maks 10 detik)")
    st.info(
        "Video diproses per-frame, **audio asli dipertahankan** otomatis. "
        "⛔ Durasi melebihi 10 detik akan ditolak — silakan potong video dulu. "
        "💎 SUPIR tidak tersedia untuk video (diffusion per-frame terlalu berat)."
    )
    vup = st.file_uploader(
        "Unggah video (MP4 / WebM / MOV / AVI)", type=["mp4", "webm", "mov", "avi", "mkv"],
        key="video_up")

    if vup:
        vtmp = os.path.join(tempfile.gettempdir(), "in_" + vup.name)
        with open(vtmp, "wb") as f:
            f.write(vup.getvalue())

        info = E.video_info(vtmp)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Durasi", f"{info['duration']:.1f} dtk")
        m2.metric("Resolusi", f"{info['w']}×{info['h']}")
        m3.metric("FPS", f"{info['fps']:.0f}")
        m4.metric("Frame", f"{info['frames']}")

        if info.get("duration", 0) > E.MAX_VIDEO_SECONDS + 0.25:
            st.error(
                f"⛔ Video durasi {info['duration']:.1f} detik melebihi batas "
                f"**{E.MAX_VIDEO_SECONDS} detik**. Potong video maksimal 10 detik, "
                f"lalu unggah ulang.")
            st.stop()

        engine = st.radio(
            "Engine",
            [e for e, _ in VIDEO_ENGINES],
            format_func=lambda e: dict(VIDEO_ENGINES)[e],
            key="video_engine",
        )

        model_key = None
        scale = 2
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            if engine == "realesrgan":
                model_key = st.selectbox(
                    "Model Real-ESRGAN",
                    ["realesrgan_x2plus", "realesrgan_x4plus", "realesrgan_anime"],
                    index=0,
                    format_func=lambda k: f"{k.replace('realesrgan_', '').upper()} — {E.SPANDREL_MODELS[k][2]}",
                    key="vid_rm")
                scale = E.SPANDREL_MODELS[model_key][1]
            elif engine in ("swinir", "cugan", "hat"):
                model_key = engine + "_x4"
                scale = 4
            elif engine == "fsrcnn":
                scale = st.selectbox("Pembesaran", [2, 3, 4],
                                     format_func=lambda s: f"{s}x", key="vid_fs_scale")
        with c2:
            frame_cap = int(info["fps"] * E.MAX_VIDEO_SECONDS)
            max_frames = st.number_input(
                "Batas frame (0 = semua, maks 10 dtk)", 0, frame_cap, 0, step=30,
                help="Uji coba cepat: isi mis. 30 = ±1 detik.", key="vid_maxf")
        with c3:
            sharpen = st.slider("Sharpening tambahan", 0, 100, 0, 5, key="vid_sharp")

        n_proc = info["frames"] if max_frames <= 0 else min(int(max_frames), info["frames"])
        if model_key:
            tiles = E.estimate_tiles(info["w"], info["h"], model_key)
            est = n_proc * tiles * E.TILE_SECONDS[model_key]
            est_text = (f"±{tiles} tile/frame × {E.TILE_SECONDS[model_key]} dtk → "
                        f"**±{est / 60:.0f} menit** untuk {n_proc} frame (CPU)")
        elif engine == "fsrcnn":
            est_text = f"±{n_proc * 0.4 / 60:.1f} menit (cepat) untuk {n_proc} frame"
        else:
            est_text = f"{n_proc} frame"

        model_ready = True
        if model_key:
            model_ready = _ensure_model_ready(model_key)
        elif engine == "fsrcnn":
            model_ready = _ensure_model_ready(scale)

        b1, b2 = st.columns([1, 3])
        with b1:
            go = st.button("🚀 Proses Video", type="primary", use_container_width=True,
                           disabled=not model_ready, key="video_go")
        with b2:
            st.caption(
                f"Hasil: {info['w'] * scale}×{info['h'] * scale} @ {info['fps']:.0f} fps. {est_text}")

        if go:
            out_path = os.path.join(tempfile.gettempdir(), f"enhanced_{int(time.time())}.mp4")
            pbar = st.progress(0.0, text="Menyiapkan…")

            def _cb(i, total, elapsed):
                pbar.progress(i / total,
                              text=f"Frame {i}/{total}  •  {elapsed:.0f} dtk  •  "
                                   f"ETA ±{elapsed / max(i, 1) * (total - i):.0f} dtk")

            try:
                res = E.process_video(
                    vtmp, out_path, "ai" if model_key else engine, model_key, scale,
                    max_frames=int(max_frames), sharpen=sharpen / 100.0,
                    keep_audio=True, progress_cb=_cb)
            except Exception as ex:
                pbar.empty()
                st.error(f"Gagal memproses video: {ex}")
                st.stop()

            pbar.progress(1.0, text="Selesai ✅")
            st.success(
                f"Selesai: {res['frames']} frame dalam {res['elapsed']:.0f} dtk"
                + (" (audio dipertahankan 🔊)" if res["audio"] else " (tanpa audio)."))

            c1, c2 = st.columns(2)
            with c1:
                st.video(vtmp, caption="Asli")
            with c2:
                st.video(out_path, caption=f"Hasil — {res['out_w']}×{res['out_h']}")

            with open(out_path, "rb") as f:
                data = f.read()
            st.download_button("⬇️ Unduh video hasil", data,
                               f"{os.path.splitext(vup.name)[0]}_enhanced.mp4",
                               "video/mp4", use_container_width=True)
            m1, m2, m3 = st.columns(3)
            m1.metric("Resolusi", f"{res['in_w']}×{res['in_h']} → {res['out_w']}×{res['out_h']}")
            m2.metric("Durasi", f"{res['frames'] / res['fps']:.1f} dtk")
            m3.metric("Ukuran", f"{len(data) / 1024 / 1024:.1f} MB")
