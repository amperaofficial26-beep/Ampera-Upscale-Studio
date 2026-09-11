"""Halaman 3 — Video Upscale: unggah, pratinjau, identitas + kualitas, model."""

import os
import tempfile
import time

import streamlit as st

import analysis as A
import enhance as E
import presets as P
import ui


def render():
    ui.brand("Video Upscale", "Video",
             "Unggah video pendek, periksa identitasnya, lalu pilih model.")

    ui.label("1 · Unggah video")
    vup = st.file_uploader("Video", type=["mp4", "webm", "mov", "avi", "mkv"],
                           label_visibility="collapsed", key="vid_up")
    st.caption(f"MP4, WebM, MOV, AVI atau MKV · maksimal {E.MAX_VIDEO_SECONDS} detik · "
               "audio asli dipertahankan")

    if not vup:
        st.write("")
        ui.note("Belum ada video. Unggah satu berkas untuk melihat analisis lengkapnya.")
        ui.footer("© Ampera Upscale — 2026")
        return

    vtmp = os.path.join(tempfile.gettempdir(), "ampera_in_" + vup.name)
    with open(vtmp, "wb") as f:
        f.write(vup.getvalue())

    info = E.video_info(vtmp)
    if not info or not info.get("frames"):
        st.error("Video tidak dapat dibaca. Coba format lain, misalnya MP4 (H.264).")
        ui.footer("© Ampera Upscale — 2026")
        return

    # ---------------------------------------------- pratinjau + identitas
    ui.label("2 · Identitas video")
    prev, ident = st.columns([1, 1.25])
    with prev:
        st.video(vtmp)
        st.caption("Pratinjau")
    with ident:
        rows = A.video_identity(vtmp, info, vup.name, vup.size)
        rows.insert(2, ("Ukuran berkas", ui.human_size(vup.size)))
        ui.identity_table(rows)

    st.write("")
    ui.label("Penilaian kualitas")
    q = A.video_quality(vtmp, info, vup.size)
    if q["metrics"]:
        ui.quality_chips(q["metrics"])
        st.write("")
    ui.score_box(q["score"], q["verdict"])

    if info["duration"] > E.MAX_VIDEO_SECONDS + 0.25:
        st.write("")
        st.error(f"Durasi {info['duration']:.1f} detik melebihi batas "
                 f"{E.MAX_VIDEO_SECONDS} detik. Potong videonya lalu unggah ulang.")
        ui.footer("© Ampera Upscale — 2026")
        return

    # ---------------------------------------------- model
    ui.label("3 · Pilihan model")
    engine, model_key, scale = P.preset_picker(P.VIDEO_PRESETS, "vid_preset")

    frame_cap = max(int(info["fps"] * E.MAX_VIDEO_SECONDS), 1)
    with st.expander("Pengaturan lanjutan"):
        if engine == "fsrcnn":
            scale = st.select_slider("Pembesaran", [2, 3, 4], value=2,
                                     format_func=lambda s: f"{s}×", key="vid_scale")
        else:
            st.caption(f"Model ini memakai pembesaran tetap {scale}×.")
        max_frames = st.number_input(
            "Batas frame (0 = semua)", 0, frame_cap, 0, step=10, key="vid_maxf",
            help="Isi angka kecil untuk uji coba cepat sebelum proses penuh.")
        sharpen = st.slider("Ketajaman tambahan", 0, 100, 0, 5, key="vid_sharp")

    # ---------------------------------------------- proses
    ui.label("4 · Proses")
    n_proc = info["frames"] if max_frames <= 0 else min(int(max_frames), info["frames"])
    if model_key:
        tiles = E.estimate_tiles(info["w"], info["h"], model_key)
        est = ui.human_time(n_proc * E.estimate_seconds(info["w"], info["h"],
                                                        model_key))
    else:
        est = ui.human_time(n_proc * 0.4)

    ready = P.ensure_model(model_key) if model_key else P.ensure_model(scale)

    rows = [("Hasil", f"{info['w'] * scale} × {info['h'] * scale}"),
            ("Kelas resolusi", A.resolution_class(info["w"] * scale, info["h"] * scale)),
            ("Frame diproses", f"{n_proc}"),
            ("Perkiraan waktu", f"± {est}")]
    if model_key and E.TILE_WORKERS > 1:
        rows.append(("Proses paralel", f"{E.TILE_WORKERS} tile sekaligus"))
    ui.stats(rows)
    st.write("")

    if st.button("Tingkatkan kualitas video", type="primary",
                 disabled=not ready, width="stretch", key="vid_go"):
        out_path = os.path.join(tempfile.gettempdir(),
                                f"ampera_out_{int(time.time())}.mp4")
        bar = st.progress(0.0, text="Menyiapkan…")

        def _cb(i, total, elapsed):
            eta = elapsed / max(i, 1) * (total - i)
            bar.progress(min(i / total, 1.0),
                         text=f"Frame {i} dari {total} · sisa ± {ui.human_time(eta)}")

        try:
            res = E.process_video(vtmp, out_path, engine, model_key, scale,
                                  max_frames=int(max_frames), sharpen=sharpen / 100.0,
                                  keep_audio=True, progress_cb=_cb)
        except Exception as ex:
            bar.empty()
            st.error(f"Gagal memproses video: {ex}")
            res = None
        else:
            bar.empty()

        if res:
            st.session_state.vid_result = {
                "path": out_path, "res": res,
                "name": os.path.splitext(vup.name)[0]}

    # ---------------------------------------------- hasil
    rs = st.session_state.get("vid_result")
    if rs and os.path.exists(rs["path"]):
        res = rs["res"]
        with open(rs["path"], "rb") as f:
            data = f.read()

        st.divider()
        ui.label("Hasil")
        ui.stats([
            ("Resolusi", f"{res['in_w']} × {res['in_h']}  →  "
                         f"{res['out_w']} × {res['out_h']}"),
            ("Frame", f"{res['frames']}"),
            ("Waktu", ui.human_time(res["elapsed"])),
            ("Audio", "dipertahankan" if res["audio"] else "tidak ada"),
            ("Ukuran", ui.human_size(len(data))),
        ])
        st.write("")
        st.video(rs["path"])
        st.caption("Hasil peningkatan")
        st.download_button("Unduh video", data, f"{rs['name']}_upscaled.mp4",
                           "video/mp4", width="stretch")

    ui.footer("© Ampera Upscale — 2026")
