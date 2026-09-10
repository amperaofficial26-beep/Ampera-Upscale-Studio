"""
💎 SUPIR — mode eksperimental (kualitas maksimal).

SUPIR (https://github.com/Fanghua-Yu/SUPIR, arXiv:2401.13627) adalah upscaler
berbasis *diffusion* (StableSR + Swin2SR control). Kode intinya di-vendor dari
repo resmi ke folder ``vendor/SUPIR``.

Persyaratan (jujur):
  * GPU NVIDIA (CUDA) dengan ±11 GB VRAM — SUPIR resmi hanya mendukung CUDA.
  * xformers (kompatibel dengan versi torch).
  * Model (total ±8.5 GB) di folder ``models/supir/``:
      - sd_xl_base_1.0_0.9vae.safetensors  (~6.9 GB)
        https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0_0.9vae.safetensors
      - SUPIR-v0Q.ckpt  (~1.4 GB)
        https://huggingface.co/stabilityai/SUPIR_V.02_3k  (atau link Google Drive di README repo)
"""

import os
import sys

import torch

HERE = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.join(HERE, "vendor", "SUPIR")
MODEL_DIR = os.path.join(HERE, "models", "supir")

SDXL_FILE = "sd_xl_base_1.0_0.9vae.safetensors"
SUPRIR_FILE = "SUPIR-v0Q.ckpt"

DEFAULT_PROMPT = (
    "Cinematic, High Contrast, highly detailed, taken using a Canon EOS R camera, "
    "hyper detailed photo - realistic maximum detail, 32k, Color Grading, ultra HD, "
    "extreme meticulous detailing, skin pore detailing, hyper sharpness, "
    "perfect without deformations."
)
NEGATIVE_PROMPT = (
    "painting, oil painting, illustration, drawing, art, sketch, oil painting, "
    "cartoon, CG Style, 3D render, unreal engine, blurring, dirty, messy, "
    "worst quality, low quality, frames, watermark, signature, jpeg artifacts, "
    "deformed, lowres, over-smooth"
)

_model = None


def _vendor_on_path():
    if VENDOR not in sys.path:
        sys.path.insert(0, VENDOR)


def missing_files():
    return [f for f in (SDXL_FILE, SUPRIR_FILE)
            if not os.path.exists(os.path.join(MODEL_DIR, f))]


def supir_status():
    """Return (siap: bool, pesan: str) — dipanggil UI untuk menampilkan status."""
    if not os.path.isdir(VENDOR):
        return False, ("Kode SUPIR belum ada (folder vendor/SUPIR). "
                       "Clone: git clone https://github.com/Fanghua-Yu/SUPIR vendor/SUPIR")
    missing = missing_files()
    if missing:
        return False, (
            "Model SUPIR belum diunduh: " + ", ".join(missing) +
            f" → simpan di folder ``models/supir/`` (total ±8.5 GB).")
    if not torch.cuda.is_available():
        return False, ("SUPIR membutuhkan GPU NVIDIA (±11 GB VRAM) — "
                       "device ini hanya punya CPU, jadi mode eksperimental "
                       "tidak dapat dijalankan di sini.")
    try:
        import xformers  # noqa: F401
    except ImportError:
        return False, "Butuh ``pip install xformers`` (kompatibel dengan versi torch)."
    return True, "SUPIR siap (GPU terdeteksi)."


def _get_model():
    global _model
    if _model is None:
        import yaml
        _vendor_on_path()
        # CLIP dipath ke None agar unduh otomatis dari HuggingFace
        import CKPT_PTH
        CKPT_PTH.LLAVA_CLIP_PATH = None
        CKPT_PTH.SDXL_CLIP1_PATH = None
        CKPT_PTH.SDXL_CLIP2_CKPT_PTH = None

        with open(os.path.join(VENDOR, "options", "SUPIR_v0.yaml")) as f:
            cfg = yaml.safe_load(f)
        cfg["SDXL_CKPT"] = os.path.join(MODEL_DIR, SDXL_FILE)
        cfg["SUPIR_CKPT_Q"] = os.path.join(MODEL_DIR, SUPRIR_FILE)
        cfg["SUPIR_CKPT_F"] = os.path.join(MODEL_DIR, "SUPIR-v0F.ckpt")
        local_yaml = os.path.join(VENDOR, "options", "SUPIR_v0_local.yaml")
        with open(local_yaml, "w") as f:
            yaml.safe_dump(cfg, f)

        from SUPIR.util import create_SUPIR_model
        m = create_SUPIR_model(local_yaml, SUPIR_sign="Q", load_default_setting=True)
        m = m.half()
        m.ae_dtype = torch.bfloat16
        m.model.dtype = torch.float16
        m = m.to("cuda")
        _model = m
    return _model


def enhance_supir(img_bgr: "np.ndarray", prompt: str = None, upscale: int = 1,
                  min_size: int = 1024, steps: int = 50, seed: int = 1234):
    """
    Jalankan SUPIR pada satu gambar BGR.
    upscale : faktor pembesaran (1 = perhalus ke min_size, 2/4 = perbesar)
    """
    import numpy as np
    from PIL import Image

    _vendor_on_path()
    from SUPIR.util import PIL2Tensor, Tensor2PIL
    m = _get_model()

    pil = Image.fromarray(img_bgr[..., ::-1])
    LQ, h0, w0 = PIL2Tensor(pil, upsacle=upscale, min_size=min_size)
    LQ = LQ.unsqueeze(0).to("cuda")[:, :3]

    clean = m.batchify_denoise(LQ)
    samples = m.batchify_sample(
        LQ, [prompt or DEFAULT_PROMPT],
        num_steps=steps, restoration_scale=-1,
        s_churn=5, s_noise=1.01, cfg_scale=7.5, control_scale=1.0,
        seed=seed, num_samples=1,
        p_p=prompt or DEFAULT_PROMPT, n_p=NEGATIVE_PROMPT,
        color_fix_type="Wavelet",
        use_linear_CFG=True, use_linear_control_scale=False,
        cfg_scale_start=4.0, control_scale_start=0.0,
    )
    out = Tensor2PIL(samples[0], h0, w0)
    return np.array(out)[..., ::-1].copy()
