"""
Engine peningkat (upscale/enhance) foto & video.

Model:
  🥇 Real-ESRGAN  — mesin utama   (torch + spandrel, tiling 256px)
  🥈 SwinIR       — mode Natural  (torch + spandrel, tiling)
  🥉 Real-CUGAN   — mode Anime    (torch + spandrel, tiling)
  🔥 HAT          — Ultra Quality (torch + spandrel, tiling)
  💎 SUPIR        — eksperimental (diffusion, GPU; lihat supir.py)
  ⚡ FSRCNN       — cepat (OpenCV dnn_superres)
  🔧 Klasik       — Lanczos + unsharp (tanpa AI)
"""

import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
import cv2
import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))


def _pick_model_dir() -> str:
    """Folder model: sisi app bila writable, selain itu /tmp (mis. deploy read-only)."""
    d = os.path.join(HERE, "models")
    try:
        os.makedirs(d, exist_ok=True)
        probe = os.path.join(d, ".__w_probe__")
        with open(probe, "w"):
            pass
        os.remove(probe)
        return d
    except OSError:
        return "/tmp/ampera_models"


MODEL_DIR = _pick_model_dir()

# ---------------------------------------------------------------- batas input
MAX_PHOTO_BYTES = 20 * 1024 * 1024      # 20 MB
MAX_VIDEO_SECONDS = 10                  # 10 detik

# ---------------------------------------------------------------- registry model
# engine foto/video -> (file bobot, scale, deskripsi pendek)
SPANDREL_MODELS = {
    "realesrgan_x4plus":  ("RealESRGAN_x4plus.pth", 4, "foto / realistis"),
    "realesrgan_anime":   ("RealESRGAN_x4plus_anime_6B.pth", 4, "animasi / ilustrasi"),
    "realesrgan_animevid": ("realesr-animevideov3.pth", 4, "fidelitas tinggi — super cepat"),
    "realesrgan_x2plus":  ("RealESRGAN_x2plus.pth", 2, "pembesaran 2x"),
    "swinir_x4":          ("SwinIR_4xSR_M_x4.pth", 4, "natural"),
    "cugan_x4":           ("RealCUGAN_up4x.pth", 4, "anime"),
    "hat_x4":             ("HAT_SRx4.pth", 4, "ultra quality"),
}
FSRCNN_MODELS = {2: "FSRCNN_x2.pb", 3: "FSRCNN_x3.pb", 4: "FSRCNN_x4.pb"}

# URL resmi/verified untuk setiap file bobot model (dipakai app & download_models.py)
MODEL_DOWNLOADS = {
    "RealESRGAN_x4plus.pth": (
        "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth",
        67108864),
    "RealESRGAN_x2plus.pth": (
        "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth",
        67108864),
    "RealESRGAN_x4plus_anime_6B.pth": (
        "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth",
        18874368),
    "realesr-animevideov3.pth": (
        "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-animevideov3.pth",
        2504012),
    "SwinIR_4xSR_M_x4.pth": (
        "https://huggingface.co/licyk/sd-upscaler-models/resolve/main/SwinIR/001_classicalSR_DIV2K_s48w8_SwinIR-M_x4.pth",
        59611499),
    "RealCUGAN_up4x.pth": (
        "https://huggingface.co/smnorini/Real_CUGAN_4x/resolve/main/Real_CUGAN_4x.pth",
        5636403),
    "HAT_SRx4.pth": (
        "https://huggingface.co/jaideepsingh/upscale_models/resolve/main/HAT/HAT_SRx4.pth",
        85137601),
    "FSRCNN_x2.pb": (
        "https://github.com/Saafke/FSRCNN_Tensorflow/raw/master/models/FSRCNN_x2.pb", 40000),
    "FSRCNN_x3.pb": (
        "https://github.com/Saafke/FSRCNN_Tensorflow/raw/master/models/FSRCNN_x3.pb", 41000),
    "FSRCNN_x4.pb": (
        "https://github.com/Saafke/FSRCNN_Tensorflow/raw/master/models/FSRCNN_x4.pb", 42000),
}


def model_path(fname: str) -> str:
    return os.path.join(MODEL_DIR, fname)


def model_size_mb(fname: str) -> float:
    """Ukuran file model (MB) dari katalog MODEL_DOWNLOADS."""
    return MODEL_DOWNLOADS.get(fname, ("", 0))[1] / 1024 / 1024


def model_missing(model_key) -> str:
    """Return nama file yang hilang untuk model_key (spandrel key / scale fsrcnn), atau None."""
    if model_key in SPANDREL_MODELS:
        fname = SPANDREL_MODELS[model_key][0]
    else:
        fname = FSRCNN_MODELS.get(model_key) or FSRCNN_MODELS.get(str(model_key))
        if fname is None:
            return None
    return fname if not os.path.exists(model_path(fname)) else None


def download_model(fname: str, progress_cb=None) -> str:
    """Unduh file model dari MODEL_DOWNLOADS. Return path hasil."""
    import urllib.request

    if fname not in MODEL_DOWNLOADS:
        raise ValueError(f"File model tidak dikenal: {fname}")
    url, size = MODEL_DOWNLOADS[fname]
    dest = model_path(fname)
    os.makedirs(MODEL_DIR, exist_ok=True)
    tmp = dest + ".part"
    with urllib.request.urlopen(url) as r:
        total = int(r.headers.get("Content-Length") or size or 0)
        done = 0
        with open(tmp, "wb") as f:
            while True:
                chunk = r.read(256 * 1024)
                if not chunk:
                    break
                f.write(chunk)
                done += len(chunk)
                if progress_cb:
                    progress_cb(done, total)
    os.replace(tmp, dest)
    return dest

# Ukuran tile per model. HAT butuh tile kecil agar tidak OOM di RAM terbatas.
TILE_OVERRIDES = {"hat_x4": 128}
DEFAULT_TILE = 256
TILE_PAD = 16

# Estimasi CPU (dtk per tile), diukur di 2 core / 2 GB RAM
TILE_SECONDS = {
    "realesrgan_x4plus": 30, "realesrgan_x2plus": 11, "realesrgan_anime": 11,
    "realesrgan_animevid": 1.5,
    "swinir_x4": 52, "cugan_x4": 4, "hat_x4": 24,
}


def cpu_count() -> int:
    return os.cpu_count() or 1


def _env_int(name: str, default: int) -> int:
    try:
        v = int(os.environ.get(name, ""))
        return v if v > 0 else default
    except (TypeError, ValueError):
        return default

TILE_WORKERS = _env_int("AMPERA_WORKERS", 2 if cpu_count() >= 2 else 1)


def tune_torch_threads() -> int:
    """Pastikan torch memakai semua core CPU."""
    n = cpu_count()
    try:
        if torch.get_num_threads() < n:
            torch.set_num_threads(n)
    except Exception:
        pass
    return torch.get_num_threads()

tune_torch_threads()

  
def tile_for(model_key: str) -> int:
    return TILE_OVERRIDES.get(model_key, DEFAULT_TILE)


def estimate_tiles(w: int, h: int, model_key: str) -> int:
    """Jumlah tile 256/128px yang dibutuhkan untuk memproses gambar w×h."""
    tile = tile_for(model_key)
    step = max(tile - 2 * TILE_PAD, 8)
    return len(_tile_starts(w, tile, step)) * len(_tile_starts(h, tile, step))


def estimate_seconds(w: int, h: int, model_key: str) -> float:
    return estimate_tiles(w, h, model_key) * TILE_SECONDS.get(model_key, 30)

from collections import OrderedDict

MAX_CACHE = 2  # model AI maksimum yang di-cache (hemat RAM di mesin kecil)
_spandrel_cache: "OrderedDict[str, tuple]" = OrderedDict()
_fsrcnn_cache: dict = {}


# ---------------------------------------------------------------- model loading
def load_spandrel(model_key: str):
    """Load (dan cache) model berbasis spandrel. Return (model, scale)."""
    if model_key not in SPANDREL_MODELS:
        raise ValueError(f"Model tidak dikenal: {model_key}")
    if model_key in _spandrel_cache:
        _spandrel_cache.move_to_end(model_key)
        return _spandrel_cache[model_key]
    import spandrel  # import berat, hanya saat dibutuhkan

    loader = spandrel.ModelLoader()
    path = os.path.join(MODEL_DIR, SPANDREL_MODELS[model_key][0])
    ckpt = torch.load(path, map_location="cpu", weights_only=False)
    if isinstance(ckpt, dict):
        sd = ckpt.get("params_ema", ckpt.get("params", ckpt))
    else:
        sd = ckpt
    model = loader.load_from_state_dict(sd).eval()
    _spandrel_cache[model_key] = (model, SPANDREL_MODELS[model_key][1])
    _spandrel_cache.move_to_end(model_key)
    while len(_spandrel_cache) > MAX_CACHE:
        _spandrel_cache.popitem(last=False)
    return _spandrel_cache[model_key]


def load_fsrcnn(scale: int):
    if scale not in FSRCNN_MODELS:
        raise ValueError(f"Scale FSRCNN harus 2/3/4, dapat {scale}")
    if scale not in _fsrcnn_cache:
        m = cv2.dnn_superres.DnnSuperResImpl_create()
        m.readModel(os.path.join(MODEL_DIR, FSRCNN_MODELS[scale]))
        m.setModel("fsrcnn", scale)
        _fsrcnn_cache[scale] = m
    return _fsrcnn_cache[scale]


def model_file_size_mb(model_key: str) -> float:
    p = os.path.join(MODEL_DIR, SPANDREL_MODELS[model_key][0])
    return os.path.getsize(p) / 1024 / 1024 if os.path.exists(p) else 0.0


# ---------------------------------------------------------------- tiling
def _side_ramp(n: int, ramp: int, ramp_start: bool, ramp_end: bool) -> np.ndarray:
    a = np.ones(n, np.float32)
    r = min(ramp, n)
    if ramp_start and r > 1:
        a[:r] = np.linspace(0.0, 1.0, r, np.float32)
    if ramp_end and r > 1:
        a[-r:] = np.linspace(0.0, 1.0, r, np.float32)[::-1]
    return a


def _tile_starts(n: int, tile: int, step: int):
    if n <= tile:
        return [0]
    starts = list(range(0, n - tile + 1, step))
    if starts[-1] != n - tile:
        starts.append(n - tile)
    return starts


def tile_process(img: np.ndarray, fn, scale: int, tile: int = None,
                 pad: int = TILE_PAD, model_key: str = None,
                 progress_cb=None) -> np.ndarray:
    """Proses gambar per-tile dengan cross-fade agar tidak ada sambungan (seam)."""
    if tile is None:
        tile = tile_for(model_key) if model_key else DEFAULT_TILE
    h, w, _ = img.shape
    step = max(tile - 2 * pad, 8)
    ys = _tile_starts(h, tile, step)
    xs = _tile_starts(w, tile, step)
    total = len(ys) * len(xs)
    out = np.zeros((h * scale, w * scale, 3), np.float32)
    wsum = np.zeros((h * scale, w * scale, 1), np.float32)
    i = 0
    for y0 in ys:
        for x0 in xs:
            y1 = min(y0 + tile, h)
            x1 = min(x0 + tile, w)
            tile_in = img[y0:y1, x0:x1]
            tile_out = fn(tile_in)
            oy0, oy1 = y0 * scale, y1 * scale
            ox0, ox1 = x0 * scale, x1 * scale
            wy = _side_ramp(oy1 - oy0, 2 * pad * scale, ramp_start=(y0 > 0),
                            ramp_end=(y1 < h))
            wx = _side_ramp(ox1 - ox0, 2 * pad * scale, ramp_start=(x0 > 0),
                            ramp_end=(x1 < w))
            wt = (wy[:, None] * wx[None, :]).astype(np.float32)
            out[oy0:oy1, ox0:ox1] += tile_out * wt[..., None]
            wsum[oy0:oy1, ox0:ox1] += wt[..., None]
            i += 1
            if progress_cb:
                progress_cb(i, total)
    out /= np.maximum(wsum, 1e-8)
    return out


def _spandrel_enhance(model_key: str, img: np.ndarray, tile: int = None,
                      pad: int = TILE_PAD, progress_cb=None) -> np.ndarray:
    if tile is None:
        tile = tile_for(model_key)
    model, scale = load_spandrel(model_key)

    def fn(t_bgr):
        rgb = t_bgr.astype(np.float32, copy=False) / 255.0
        rgb = np.ascontiguousarray(rgb[..., ::-1])
        x = torch.from_numpy(rgb).permute(2, 0, 1).unsqueeze(0)
        with torch.no_grad(), torch.inference_mode():
            y = model(x).clamp(0, 1)
        y = y.squeeze(0).permute(1, 2, 0).numpy().astype(np.float32)
        y *= 255.0
        return np.ascontiguousarray(y[..., ::-1])  # BGR

    out = tile_process(img, fn, scale, tile=tile, pad=pad, progress_cb=progress_cb)
    return np.clip(out, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- post process
def unsharp(img: np.ndarray, amount: float, sigma: float = 1.0) -> np.ndarray:
    if amount <= 0:
        return img
    blur = cv2.GaussianBlur(img, (0, 0), sigma)
    return cv2.addWeighted(img, 1.0 + amount, blur, -amount, 0)


# ---------------------------------------------------------------- engine: image
def enhance_fsrcnn(img: np.ndarray, scale: int) -> np.ndarray:
    return load_fsrcnn(scale).upsample(img)


def enhance_classic(img: np.ndarray, scale: int) -> np.ndarray:
    h, w = img.shape[:2]
    return cv2.resize(img, (w * scale, h * scale), interpolation=cv2.INTER_LANCZOS4)


def enhance_image(img: np.ndarray, engine: str, model_key: str = None,
                  scale: int = 2, sharpen: float = 0.0,
                  progress_cb=None) -> np.ndarray:
    """
    engine : 'ai' (pakai model_key dari SPANDREL_MODELS), 'fsrcnn', 'classic'
    """
    if engine == "ai":
        if not model_key:
            raise ValueError("Engine 'ai' membutuhkan model_key.")
        out = _spandrel_enhance(model_key, img, progress_cb=progress_cb)
    elif engine == "fsrcnn":
        out = enhance_fsrcnn(img, scale)
    elif engine == "classic":
        out = enhance_classic(img, scale)
    else:
        raise ValueError(f"Engine tidak dikenal: {engine}")
    if sharpen > 0:
        out = unsharp(out, sharpen)
    return out


# ---------------------------------------------------------------- ffmpeg helper
def _ffmpeg() -> str:
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def has_audio(path: str) -> bool:
    try:
        r = subprocess.run([_ffmpeg(), "-hide_banner", "-i", path],
                           capture_output=True, text=True, timeout=30)
        return "Audio:" in (r.stderr or "")
    except Exception:
        return False

def to_h264(src: str, dst: str) -> bool:
    """
    Re-encode ke H.264 + yuv420p + faststart.

    OpenCV VideoWriter hanya bisa menulis 'mp4v' (MPEG-4 Part 2) yang TIDAK bisa
    diputar oleh Chrome/Safari di tag <video>. Tanpa langkah ini hasil video
    tampak "gagal" di UI walau file-nya sebenarnya valid.
    """
    try:
        r = subprocess.run(
            [_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error", "-i", src,
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
             "-pix_fmt", "yuv420p", "-movflags", "+faststart", dst],
            capture_output=True, text=True, timeout=1800)
        return r.returncode == 0 and os.path.exists(dst) and os.path.getsize(dst) > 1000
    except Exception:
        return False


def mux_audio(video_noaudio: str, video_orig: str, dst: str) -> bool:
    """Gabungkan video hasil proses dengan audio dari video asli."""
    tmp_audio = dst + ".audio.m4a"
    try:
        r = subprocess.run(
            [_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error",
             "-i", video_orig, "-vn", "-acodec", "aac", "-b:a", "192k", tmp_audio],
            capture_output=True, text=True, timeout=600)
        if r.returncode != 0 or not os.path.exists(tmp_audio) or os.path.getsize(tmp_audio) < 1000:
            return False
        r = subprocess.run(
            [_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error",
             "-i", video_noaudio, "-i", tmp_audio,
             "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac",
             "-shortest", dst + ".tmp.mp4"],
            capture_output=True, text=True, timeout=600)
        if r.returncode == 0:
            os.replace(dst + ".tmp.mp4", dst)
            return True
        return False
    except Exception:
        return False
    finally:
        if os.path.exists(tmp_audio):
            os.remove(tmp_audio)


# ---------------------------------------------------------------- video
def process_video(src: str, dst: str, engine: str, model_key: str = None,
                  scale: int = 2, max_frames: int = 0,
                  sharpen: float = 0.0, keep_audio: bool = True,
                  progress_cb=None) -> dict:
    """Proses video frame-per-frame. Return info dict."""
    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        raise RuntimeError("Gagal membuka video.")
        fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
    if not fps or fps != fps or fps <= 0 or fps > 240:
        fps = 30.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    n = total if max_frames <= 0 else min(total, max_frames)

    raw = dst + ".raw.mp4"     # tulisan mentah OpenCV (mp4v), lalu di-transcode
    vw = cv2.VideoWriter(raw, cv2.VideoWriter_fourcc(*"mp4v"), fps,
                         (w * scale, h * scale))
    t0 = time.time()
    frames = 0
    try:
        for i in range(n):
            ok, frame = cap.read()
            if not ok:
                break
            out = enhance_image(frame, engine, model_key, scale, sharpen=sharpen)
            vw.write(out)
            frames += 1
            if progress_cb:
                progress_cb(frames, n, time.time() - t0)
    finally:
        cap.release()
        vw.release()
    if frames == 0:
        if os.path.exists(raw):
            os.remove(raw)
        raise RuntimeError("Tidak ada frame yang bisa dibaca dari video ini.")

    # H.264 supaya bisa diputar langsung di browser (st.video)
    if to_h264(raw, dst):
        os.remove(raw)
    else:
        os.replace(raw, dst)   # fallback: pakai mp4v, tetap bisa diunduh
    audio = False
    if keep_audio and frames > 0:
        audio = has_audio(src)
        if audio:
            audio = mux_audio(dst, src, dst)

    return {
        "fps": fps, "in_w": w, "in_h": h,
        "out_w": w * scale, "out_h": h * scale,
        "frames": frames, "total": total,
        "elapsed": time.time() - t0, "audio": audio,
    }


# ---------------------------------------------------------------- util
def video_info(path: str) -> dict:
    """Metadata video. fps selalu > 0 (fallback 30) agar UI tidak pernah bagi-nol."""
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        return {}
    fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
    if not fps or fps != fps or fps <= 0 or fps > 240:   # 0, NaN, atau nilai janggal
        fps = 30.0
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    info = {
        "fps": fps,
        "w": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "h": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "frames": max(frames, 0),
    }
    info["duration"] = info["frames"] / fps
    cap.release()
    return info

def decode_image(data: bytes) -> np.ndarray:
    arr = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Gagal membaca gambar.")
    return img


def encode_image(img: np.ndarray, fmt: str = ".png") -> bytes:
    ok, buf = cv2.imencode(fmt, img)
    if not ok:
        raise RuntimeError("Gagal meng-encode gambar.")
    return buf.tobytes()
