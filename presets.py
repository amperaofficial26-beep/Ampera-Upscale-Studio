"""
Katalog preset model + helper yang dipakai bersama oleh halaman
Foto dan Video.

Satu preset = satu baris pilihan di UI:
    key: (judul, keterangan, engine, model_key, scale bawaan)
Urutan penting: preset pertama = bawaan, jadi taruh yang paling
ringan-cepat di atas supaya pengalaman pertama tidak berat.
"""

import streamlit as st

import enhance as E
import ui

PHOTO_PRESETS = {
    "balanced":  ("Seimbang", "Real-ESRGAN AnimeVideoV3 · cepat & tajam (disarankan)",
                  "ai", "realesrgan_animevid", 4),
    "quality":   ("Kualitas terbaik", "Real-ESRGAN 6B · paling detail, paling lambat",
                  "ai", "realesrgan_anime", 4),
    "anime":     ("Anime & ilustrasi", "Real-CUGAN · garis bersih untuk gambar 2D",
                  "ai", "cugan_x4", 4),
    "fast":      ("Cepat", "FSRCNN · hasil instan, detail seadanya",
                  "fsrcnn", None, 2),
    "classic":   ("Tanpa AI", "Lanczos + unsharp · pembesaran klasik",
                  "classic", None, 2),
}

VIDEO_PRESETS = {
    "balanced":  ("Seimbang", "Real-ESRGAN AnimeVideoV3 · pilihan terbaik untuk video",
                  "ai", "realesrgan_animevid", 4),
    "quality":   ("Kualitas terbaik", "Real-ESRGAN 6B · sangat lambat di CPU",
                  "ai", "realesrgan_anime", 4),
    "anime":     ("Anime & ilustrasi", "Real-CUGAN · garis bersih untuk gambar 2D",
                  "ai", "cugan_x4", 4),
    "fast":      ("Cepat", "FSRCNN · hasil instan, detail seadanya",
                  "fsrcnn", None, 2),
}

AUTO_DL_LIMIT = 5 * 1024 * 1024   # model ≤ 5 MB diunduh otomatis (sekali per sesi)


def preset_available(preset: tuple) -> bool:
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
    avail = {k: preset_available(presets[k]) for k in keys}

    def fmt(k):
        title, desc, *_ = presets[k]
        suffix = "" if avail[k] else " · perlu unduh model"
        return f"**{title}** — {desc}{suffix}"

    choice = st.radio("Model", keys, index=0, format_func=fmt,
                      label_visibility="collapsed", key=key)
    _, _, engine, model_key, scale = presets[choice]
    return engine, model_key, scale


def ensure_model(model_key) -> bool:
    """True bila bobot model siap dipakai. Model kecil (≤5 MB) diunduh
    otomatis sekali — model besar tetap lewat tombol manual."""
    missing = E.model_missing(model_key)
    if missing is None:
        return True

    size = E.MODEL_DOWNLOADS[missing][1]
    flag = "dl_auto_" + missing

    if size <= AUTO_DL_LIMIT and not st.session_state.get(flag):
        st.session_state[flag] = True
        with st.spinner(f"Menyiapkan model {missing} ({ui.human_size(size)}) — sekali saja…"):
            try:
                E.download_model(missing)
            except Exception as ex:
                st.warning(f"Unduh otomatis gagal: {ex}. Coba tombol di bawah.")

    if E.model_missing(model_key) is None:
        return True

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
