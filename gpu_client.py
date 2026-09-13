"""
Mode GPU pengguna (browser) — proses upscale di GPU milik pengunjung.

Alur:
    1. Halaman memanggil ask_gpu("video"/"image") saat user memilih mode GPU.
    2. Muncul dialog konfirmasi (st.dialog): "Gas" atau "Nggak jadi",
       lengkap dengan hasil deteksi GPU di browser user.
    3. Bila "Gas": komponen GPU disematkan — berkas TIDAK diunggah ke server.
       Model Real-CUGAN 4x (fp16 ONNX, ±2,9 MB) ikut disematkan sebagai
       base64, inferensi berjalan di WebGPU (fallback: WASM/CPU).
       Video: frame diambil via <video>+seek, di-encode H.264 (WebCodecs)
       dan dimux bersama audio AAC hasil decodeAudioData.

Berkas:
    gpu_detect.js    → deteksi nama GPU (WebGPU adapter / WebGL renderer)
    gpu_processor.js → mesin proses video/foto di sisi browser
    models/RealCUGAN_up4x_fp16.onnx → bobot model untuk browser
"""

import base64
import os

import streamlit as st
import streamlit.components.v1 as components

import enhance as E

HERE = os.path.dirname(os.path.abspath(__file__))

ONNX_FNAME = "RealCUGAN_up4x_fp16.onnx"
ORT_CDN = "https://cdn.jsdelivr.net/npm/onnxruntime-web@1.19.2/dist/"
MP4_MUXER_CDN = "https://cdn.jsdelivr.net/npm/mp4-muxer@5.1.3/+esm"

# Batas hasil per mode (juta piksel output) — khusus jalur GPU browser
VIDEO_MAX_OUT_MP = 12
IMAGE_MAX_OUT_MP = 16

_cfg = {}


# ---------------------------------------------------------------- model
def _model_b64() -> str:
    if "b64" not in _cfg:
        path = os.path.join(E.MODEL_DIR, ONNX_FNAME)
        if not os.path.exists(path):
            path = _export_onnx()
        with open(path, "rb") as f:
            _cfg["b64"] = base64.b64encode(f.read()).decode("ascii")
    return _cfg["b64"]


def _export_onnx() -> str:
    """Fallback: export Real-CUGAN ke ONNX fp16 saat file belum ada."""
    import torch

    desc, _ = E.load_spandrel("cugan_x4")
    net = desc.model.eval()

    class _Wrap(torch.nn.Module):
        def __init__(self, m):
            super().__init__()
            self.net = m

        def forward(self, x):
            return self.net(x, 1.0)

    tmp = os.path.join(E.MODEL_DIR, "cugan_fp32.onnx")
    dst = os.path.join(E.MODEL_DIR, ONNX_FNAME)
    torch.onnx.export(_Wrap(net).eval(), torch.rand(1, 3, 270, 480), tmp,
                      opset_version=13, input_names=["input"],
                      output_names=["output"],
                      dynamic_axes={"input": {0: "batch", 2: "h", 3: "w"},
                                    "output": {0: "batch", 2: "h", 3: "w"}},
                      do_constant_folding=True, dynamo=False)
    import onnx
    from onnxconverter_common import float16

    m16 = float16.convert_float_to_float16(onnx.load(tmp), keep_io_types=True)
    onnx.save(m16, dst)
    os.remove(tmp)
    return dst


# ---------------------------------------------------------------- HTML
_STYLE = """
#amp-gpu, .amp-gpu-box { all: initial; }
.amp-gpu-box * { box-sizing: border-box; font-family: Inter, -apple-system,
  "Segoe UI", Roboto, Arial, sans-serif; }
.amp-gpu-box {
  display: block; color: #B7BEC8; font-size: 14px; line-height: 1.5;
  border: 1px solid rgba(255,255,255,.09); border-radius: 14px;
  background: rgba(23,26,30,.85); padding: 16px 18px;
}
.amp-gpu-box .hd { display: flex; justify-content: space-between; gap: 12px;
  align-items: baseline; margin-bottom: 10px; }
.amp-gpu-box .ttl { font-weight: 650; color: #E8EBEF; font-size: 15px; }
.amp-gpu-box .gpu { font-size: 12px; color: #9AA2AD; }
.amp-gpu-box .gpu.ok { color: #8AD3A9; }
.amp-gpu-box .gpu.warn { color: #E3CD82; }
.amp-gpu-box .row { display: flex; gap: 10px; margin-bottom: 12px; flex-wrap: wrap; }
.amp-gpu-box input[type=file] {
  flex: 1; min-width: 200px; color: #B7BEC8; font-size: 13px;
  border: 1px dashed rgba(255,255,255,.16); border-radius: 10px;
  background: rgba(255,255,255,.02); padding: 8px 10px;
}
.amp-gpu-box button {
  border: 0; border-radius: 10px; padding: 9px 18px; font-size: 14px;
  font-weight: 650; background: #E8EBEF; color: #14171B; cursor: pointer;
}
.amp-gpu-box button:disabled { opacity: .55; cursor: default; }
.amp-gpu-box .barwrap { height: 8px; border-radius: 6px; overflow: hidden;
  background: rgba(255,255,255,.07); margin-bottom: 10px; }
.amp-gpu-box #bar { height: 100%; width: 0%;
  background: linear-gradient(90deg, #A7AFBB, #FFFFFF); transition: width .2s; }
.amp-gpu-box .stat { min-height: 20px; color: #D9DEE5; font-size: 13px; }
.amp-gpu-box .log { color: #9AA2AD; font-size: 12px; margin-top: 2px; min-height: 16px; }
.amp-gpu-box .dl {
  display: none; margin-top: 12px; text-decoration: none;
  border: 1px solid rgba(255,255,255,.2); border-radius: 10px;
  padding: 9px 16px; color: #E8EBEF; font-size: 13px; font-weight: 600;
}
.amp-gpu-box .dl:hover { background: rgba(255,255,255,.06); }
"""


def _read_js(fname: str) -> str:
    with open(os.path.join(HERE, fname), encoding="utf-8") as f:
        return f.read()


def detect_html() -> str:
    """Komponen kecil: satu baris hasil deteksi GPU user."""
    return (
        "<style>" + _STYLE + "</style>"
        '<div class="amp-gpu-box" style="padding:8px 14px;">'
        '<div id="gpu" class="gpu">Mendeteksi GPU…</div></div>'
        "<script>" + _read_js("gpu_detect.js") + "</script>"
    )


def processor_html(mode: str) -> str:
    """Komponen utama mode GPU (video / image)."""
    if mode == "video":
        title = "Proses di GPU Anda — Video"
        accept = "video/mp4,video/webm,video/quicktime,video/x-matroska"
        go = "Gas — proses sekarang"
        max_sec, max_mp = E.MAX_VIDEO_SECONDS, VIDEO_MAX_OUT_MP
    else:
        title = "Proses di GPU Anda — Foto"
        accept = "image/png,image/jpeg,image/webp,image/bmp"
        go = "Gas — proses sekarang"
        max_sec, max_mp = 0, IMAGE_MAX_OUT_MP

    js = (_read_js("gpu_processor.js")
          .replace("__MP4_MUXER_CDN__", MP4_MUXER_CDN)
          .replace("__MODE__", mode)
          .replace("__MAX_SECONDS__", str(max_sec))
          .replace("__MAX_OUT_MP__", str(max_mp))
          .replace("__ORT_CDN__", ORT_CDN))

    return (
        "<style>" + _STYLE + "</style>"
        '<div class="amp-gpu-box">'
        '<div class="hd"><span class="ttl">' + title + "</span>"
        '<span id="gpu" class="gpu">Mendeteksi GPU…</span></div>'
        '<div class="row">'
        '<input id="file" type="file" accept="' + accept + '">'
        '<button id="go" type="button">' + go + "</button></div>"
        '<div class="barwrap"><div id="bar"></div></div>'
        '<div id="stat" class="stat"></div><div id="log" class="log"></div>'
        '<a id="dl" class="dl" download>Unduh hasil</a>'
        "</div>"
        "<script>window.__MODEL_B64__=\"" + _model_b64() + "\";</script>"
        "<script src=\"" + ORT_CDN + "ort.min.js\"></script>"
        "<script type=\"module\">" + js + "</script>"
    )


def _embed_html(body: str, height: int) -> None:
    """Sematkan HTML — pakai st.iframe bila tersedia, fallback components.html."""
    iframe = getattr(st, "iframe", None)
    if iframe is not None:
        try:
            iframe(body, height=height)
            return
        except Exception:
            pass
    components.html(body, height=height)


# ---------------------------------------------------------------- dialog
@st.dialog("Proses di GPU Anda?")
def _confirm_dialog(mode: str):
    label = "video" if mode == "video" else "foto"
    st.markdown(
        f"**Proses {label} ini akan menggunakan GPU Anda** — berkas diproses "
        "sepenuhnya di peramban dan **tidak diunggah** ke server.\n\n"
        "Kecepatan proses mungkin bergantung pada model GPU yang Anda pakai.")
    try:
        _embed_html(detect_html(), 44)
    except Exception:
        pass
    c1, c2 = st.columns(2)
    if c1.button("Gas", type="primary", width="stretch", key=f"gpu_yes_{mode}"):
        st.session_state.gpu_ask = None
        st.session_state.gpu_go = mode
        st.rerun()
    if c2.button("Nggak jadi", width="stretch", key=f"gpu_no_{mode}"):
        st.session_state.gpu_ask = None
        st.rerun()


def ask_gpu(mode: str, button_label: str = "Proses dengan GPU saya",
            button_key: str = None, primary: bool = True) -> None:
    """Tombol ajukan + dialog konfirmasi + (bila Gas) panel proses GPU.

    Dipanggil dari halaman; `mode` = "video" atau "image".
    """
    if st.button(button_label, type="primary" if primary else "secondary",
                 width="stretch", key=button_key or f"gpu_ask_{mode}"):
        st.session_state.gpu_ask = mode
        st.rerun()

    if st.session_state.get("gpu_ask") == mode:
        _confirm_dialog(mode)

    if st.session_state.get("gpu_go") == mode:
        st.markdown(
            f"<small>Berkas tidak diunggah ke server — diproses penuh di "
            f"GPU perangkat Anda. Hasil otomatis terunduh setelah selesai.</small>",
            unsafe_allow_html=True)
        _embed_html(processor_html(mode),
                    430 if mode == "image" else 470)
        if st.button("Tutup panel GPU", key=f"gpu_close_{mode}"):
            st.session_state.gpu_go = None
            st.rerun()
