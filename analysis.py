"""
Analisis identitas & kualitas berkas (foto / video).

Dipakai halaman Image Upscale dan Video Upscale untuk menampilkan
"identitas lengkap sampai kualitasnya" sebelum proses dijalankan.
Semua pengukuran murni dari OpenCV/ffmpeg — tidak ada layanan eksternal.
"""

import json
import math
import os
import subprocess

import cv2
import numpy as np


# ---------------------------------------------------------------- util umum
def aspect_ratio(w: int, h: int) -> str:
    """Rasio aspek yang disederhanakan, mis. '16:9'."""
    if not w or not h:
        return "—"
    g = math.gcd(w, h)
    rw, rh = w // g, h // g
    if rw > 50 or rh > 50:          # rasio janggal → tampilkan desimal
        return f"{w / h:.2f}:1"
    return f"{rw}:{rh}"


def resolution_class(w: int, h: int) -> str:
    """Label kelas resolusi berdasarkan sisi terpanjang."""
    side = max(w, h)
    if side >= 7000:
        return "8K"
    if side >= 3400:
        return "4K / UHD"
    if side >= 2400:
        return "2K / QHD"
    if side >= 1800:
        return "Full HD"
    if side >= 1200:
        return "HD"
    if side >= 600:
        return "SD"
    return "Sangat kecil"


# ---------------------------------------------------------------- foto
def sharpness_score(img: np.ndarray) -> float:
    """Varians Laplacian — makin tinggi makin tajam (di bawah ~60 = blur)."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def noise_score(img: np.ndarray) -> float:
    """Estimasi derau: median absolute deviation dari high-pass."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    blur = cv2.GaussianBlur(gray, (0, 0), 1.2)
    return float(np.median(np.abs(gray - blur)))


def quality_verdict(img: np.ndarray, num_bytes: int) -> dict:
    """
    Ringkasan kualitas foto: ketajaman, derau, pencahayaan, kontras,
    kepadatan data (bit per piksel), plus satu kesimpulan singkat.
    """
    h, w = img.shape[:2]
    pixels = max(w * h, 1)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    sharp = sharpness_score(img)
    noise = noise_score(img)
    bright = float(gray.mean())
    contrast = float(gray.std())
    bpp = (num_bytes * 8) / pixels          # bit per piksel

    if sharp < 40:
        s_label, s_tone = "Buram", "bad"
    elif sharp < 120:
        s_label, s_tone = "Agak lembut", "warn"
    elif sharp < 600:
        s_label, s_tone = "Tajam", "good"
    else:
        s_label, s_tone = "Sangat tajam", "good"

    if noise < 1.2:
        n_label, n_tone = "Bersih", "good"
    elif noise < 3.0:
        n_label, n_tone = "Sedikit derau", "warn"
    else:
        n_label, n_tone = "Berderau", "bad"

    if bright < 55:
        b_label, b_tone = "Gelap", "warn"
    elif bright > 200:
        b_label, b_tone = "Terlalu terang", "warn"
    else:
        b_label, b_tone = "Seimbang", "good"

    c_label, c_tone = (("Datar", "warn") if contrast < 35
                       else ("Baik", "good") if contrast < 80
                       else ("Tinggi", "good"))

    if bpp < 0.6:
        k_label, k_tone = "Kompresi berat", "bad"
    elif bpp < 2.0:
        k_label, k_tone = "Kompresi wajar", "warn"
    else:
        k_label, k_tone = "Detail padat", "good"

    # skor gabungan 0-100 untuk satu kalimat kesimpulan
    score = 0
    score += min(sharp / 400, 1.0) * 45
    score += max(0.0, 1.0 - noise / 5.0) * 20
    score += min(contrast / 70, 1.0) * 15
    score += min(bpp / 3.0, 1.0) * 20

    if score >= 70:
        verdict = "Kualitas sumber sudah baik — upscale akan menambah ketajaman detail."
    elif score >= 45:
        verdict = "Kualitas menengah — cocok ditingkatkan, hasil akan terasa bedanya."
    else:
        verdict = "Kualitas rendah — paling terasa manfaatnya bila di-upscale."

    return {
        "metrics": [
            ("Ketajaman", s_label, f"{sharp:.0f}", s_tone),
            ("Derau", n_label, f"{noise:.2f}", n_tone),
            ("Pencahayaan", b_label, f"{bright:.0f}/255", b_tone),
            ("Kontras", c_label, f"{contrast:.0f}", c_tone),
            ("Kepadatan data", k_label, f"{bpp:.2f} bpp", k_tone),
        ],
        "score": round(score),
        "verdict": verdict,
    }


def image_identity(img: np.ndarray, name: str, num_bytes: int) -> list:
    """Identitas teknis foto: [(label, nilai), ...]."""
    h, w = img.shape[:2]
    ch = img.shape[2] if img.ndim == 3 else 1
    mp = (w * h) / 1_000_000
    ext = os.path.splitext(name)[1].lstrip(".").upper() or "—"
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    is_mono = bool(np.allclose(img[..., 0], gray, atol=6) and
                   np.allclose(img[..., 1], gray, atol=6))
    return [
        ("Nama berkas", name),
        ("Format", ext),
        ("Dimensi", f"{w} × {h} px"),
        ("Megapiksel", f"{mp:.2f} MP".replace(".", ",")),
        ("Rasio aspek", aspect_ratio(w, h)),
        ("Kelas resolusi", resolution_class(w, h)),
        ("Kanal warna", f"{ch} kanal ({'Grayscale' if is_mono else 'Warna RGB'})"),
        ("Kedalaman bit", f"{img.dtype.itemsize * 8} bit / kanal"),
        ("Orientasi", "Lanskap" if w > h else "Potret" if h > w else "Persegi"),
    ]


# ---------------------------------------------------------------- video
def _ffprobe(path: str) -> dict:
    """Metadata video via ffprobe bawaan imageio-ffmpeg (boleh gagal)."""
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        probe = exe.replace("ffmpeg", "ffprobe")
        if not os.path.exists(probe):
            return {}
        r = subprocess.run(
            [probe, "-v", "quiet", "-print_format", "json",
             "-show_format", "-show_streams", path],
            capture_output=True, text=True, timeout=60)
        return json.loads(r.stdout) if r.returncode == 0 else {}
    except Exception:
        return {}


def _codec_from_ffmpeg(path: str) -> dict:
    """Cadangan bila ffprobe tidak tersedia: baca dari stderr ffmpeg."""
    out = {}
    try:
        import imageio_ffmpeg
        r = subprocess.run(
            [imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-i", path],
            capture_output=True, text=True, timeout=60)
        for line in (r.stderr or "").splitlines():
            line = line.strip()
            if line.startswith("Stream") and "Video:" in line:
                out["vcodec"] = line.split("Video:")[1].split(",")[0].strip().split(" ")[0]
            elif line.startswith("Stream") and "Audio:" in line:
                out["acodec"] = line.split("Audio:")[1].split(",")[0].strip().split(" ")[0]
            elif line.startswith("Duration:") and "bitrate:" in line:
                out["bitrate"] = line.split("bitrate:")[1].strip()
    except Exception:
        pass
    return out


def video_identity(path: str, info: dict, name: str, num_bytes: int) -> list:
    """Identitas teknis video: [(label, nilai), ...]."""
    w, h = info.get("w", 0), info.get("h", 0)
    fps = info.get("fps", 0)
    frames = info.get("frames", 0)
    dur = info.get("duration", 0)

    vcodec = acodec = bitrate = None
    has_audio = None
    pr = _ffprobe(path)
    if pr:
        for s in pr.get("streams", []):
            if s.get("codec_type") == "video" and not vcodec:
                vcodec = s.get("codec_name", "").upper() or None
            if s.get("codec_type") == "audio" and not acodec:
                acodec = s.get("codec_name", "").upper() or None
                has_audio = True
        br = pr.get("format", {}).get("bit_rate")
        if br:
            bitrate = f"{int(br) / 1_000_000:.2f} Mbps".replace(".", ",")
    if not vcodec:
        fb = _codec_from_ffmpeg(path)
        vcodec = (fb.get("vcodec") or "—").upper()
        acodec = (fb.get("acodec") or "").upper() or None
        bitrate = bitrate or fb.get("bitrate")
    if has_audio is None:
        has_audio = bool(acodec)
    if not bitrate and dur:
        bitrate = f"{(num_bytes * 8 / dur) / 1_000_000:.2f} Mbps".replace(".", ",")

    return [
        ("Nama berkas", name),
        ("Kontainer", os.path.splitext(name)[1].lstrip(".").upper() or "—"),
        ("Codec video", vcodec or "—"),
        ("Durasi", f"{dur:.2f} detik".replace(".", ",")),
        ("Dimensi", f"{w} × {h} px"),
        ("Rasio aspek", aspect_ratio(w, h)),
        ("Kelas resolusi", resolution_class(w, h)),
        ("Frame rate", f"{fps:.2f} fps".replace(".", ",")),
        ("Total frame", f"{frames}"),
        ("Bitrate", bitrate or "—"),
        ("Audio", f"Ada ({acodec})" if has_audio and acodec else
                  "Ada" if has_audio else "Tidak ada"),
    ]


def video_quality(path: str, info: dict, num_bytes: int, samples: int = 5) -> dict:
    """Kualitas video dari beberapa frame contoh (ketajaman, derau, bitrate/piksel)."""
    cap = cv2.VideoCapture(path)
    frames = max(info.get("frames", 0), 1)
    picks = [int(frames * p) for p in (0.1, 0.3, 0.5, 0.7, 0.9)][:samples]
    sharps, noises, brights = [], [], []
    for idx in picks:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, fr = cap.read()
        if not ok:
            continue
        sharps.append(sharpness_score(fr))
        noises.append(noise_score(fr))
        brights.append(float(cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY).mean()))
    cap.release()

    if not sharps:
        return {"metrics": [], "score": 0,
                "verdict": "Frame contoh tidak dapat dibaca untuk analisis kualitas."}

    sharp = sum(sharps) / len(sharps)
    noise = sum(noises) / len(noises)
    bright = sum(brights) / len(brights)
    w, h = info.get("w", 1), info.get("h", 1)
    dur = max(info.get("duration", 0.001), 0.001)
    bpp = (num_bytes * 8) / max(w * h * info.get("fps", 30) * dur, 1)

    s_label, s_tone = (("Buram", "bad") if sharp < 40
                       else ("Agak lembut", "warn") if sharp < 120
                       else ("Tajam", "good"))
    n_label, n_tone = (("Bersih", "good") if noise < 1.2
                       else ("Sedikit derau", "warn") if noise < 3.0
                       else ("Berderau", "bad"))
    b_label, b_tone = (("Gelap", "warn") if bright < 55
                       else ("Terlalu terang", "warn") if bright > 200
                       else ("Seimbang", "good"))
    k_label, k_tone = (("Kompresi berat", "bad") if bpp < 0.04
                       else ("Kompresi wajar", "warn") if bpp < 0.12
                       else ("Detail padat", "good"))

    score = (min(sharp / 400, 1.0) * 50 + max(0.0, 1 - noise / 5) * 25 +
             min(bpp / 0.2, 1.0) * 25)
    verdict = ("Sumber sudah bagus — upscale menambah ketajaman." if score >= 70
               else "Kualitas menengah — peningkatan akan terlihat jelas." if score >= 45
               else "Kualitas rendah — paling besar manfaatnya bila ditingkatkan.")

    return {
        "metrics": [
            ("Ketajaman", s_label, f"{sharp:.0f}", s_tone),
            ("Derau", n_label, f"{noise:.2f}", n_tone),
            ("Pencahayaan", b_label, f"{bright:.0f}/255", b_tone),
            ("Kepadatan data", k_label, f"{bpp:.3f} bpp", k_tone),
        ],
        "score": round(score),
        "verdict": verdict,
    }
