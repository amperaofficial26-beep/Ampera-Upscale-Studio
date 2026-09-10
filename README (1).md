# ✨ Ampera Enhance (by Ampera Official)

Aplikasi Streamlit untuk memperbesar & meningkatkan kualitas **foto** dan **video**
dengan 5 model SOTA + 2 fallback:

| Model | Peran | Teknologi | Kecepatan CPU (per tile) |
|---|---|---|---|
| 🥇 **Real-ESRGAN** | **Mesin utama** | RRDBNet (torch + spandrel), tile 256px | 30 dtk (x4) / 11 dtk (x2) |
| 🥈 **SwinIR** | Mode **Natural** | Swin Transformer SR (spandrel), tile 256px | ±52 dtk (x4) |
| 🥉 **Real-CUGAN** | Mode **Anime** | CUGAN residual dense (spandrel) | ±4 dtk (x4) — paling ringan |
| 🔥 **HAT** | **Ultra Quality** | Hybrid Attention Transformer (spandrel), tile 128px (hemat RAM) | ±24 dtk per tile 128px |
| 💎 **SUPIR** | **Eksperimental** (kualitas maksimal) | Diffusion StableSR + Swin2SR control — **butuh GPU ±11 GB VRAM** | menit (GPU) |
| ⚡ FSRCNN | Cepat (disarankan video di CPU) | OpenCV dnn_superres | ±0,1–0,5 dtk/frame |
| 🔧 Klasik | Fallback tanpa AI | Lanczos + unsharp | instan |

## Batas input
- 📷 **Foto maksimal 20 MB**
- 🎬 **Video maksimal 10 detik** (durasi lebih ditolak; audio asli dipertahankan otomatis)

## Fitur
- Pratinjau sebelum/sesudah + unduh (PNG/JPG/MP4)
- Estimasi waktu & jumlah tile ditampilkan **sebelum** proses (diukur dari CPU aktual)
- Tiling 256px (128px untuk HAT) dengan cross-fade → bebas sambungan, hemat RAM
- LRU cache model (maks 2 model) agar aman di mesin 2 GB RAM
- Progress bar + ETA per frame untuk video
- SUPIR terintegrasi penuh (kode resmi di `vendor/SUPIR`) — otomatis aktif bila GPU + model tersedia

## Menjalankan

```bash
pip install -r requirements.txt
# torch CPU (tanpa GPU):
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Bobot model (sekali saja) → folder models/
curl -LO https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth
curl -LO https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth
curl -LO https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth
curl -LO https://huggingface.co/licyk/sd-upscaler-models/resolve/main/SwinIR/001_classicalSR_DIV2K_s48w8_SwinIR-M_x4.pth -o models/SwinIR_4xSR_M_x4.pth
curl -LO https://huggingface.co/smnorini/Real_CUGAN_4x/resolve/main/Real_CUGAN_4x.pth -o models/RealCUGAN_up4x.pth
curl -LO https://huggingface.co/jaideepsingh/upscale_models/resolve/main/HAT/HAT_SRx4.pth -o models/HAT_SRx4.pth
for s in 2 3 4; do curl -LO https://github.com/Saafke/FSRCNN_Tensorflow/raw/master/models/FSRCNN_x${s}.pb; done

streamlit run app.py   # buka http://localhost:8501
```

## 💎 Mode SUPIR (eksperimental)
Butuh semua ini agar aktif:
1. GPU NVIDIA ±11 GB VRAM (SUPIR resmi hanya mendukung CUDA)
2. `pip install xformers` (kompatibel versi torch Anda)
3. Model (±8,5 GB) di `models/supir/`:
   - `sd_xl_base_1.0_0.9vae.safetensors` — https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0_0.9vae.safetensors
   - `SUPIR-v0Q.ckpt` — https://huggingface.co/stabilityai/SUPIR_V.02_3k
Kode SUPIR di-vendor dari https://github.com/Fanghua-Yu/SUPIR (folder `vendor/SUPIR`).
Selama persyaratannya belum terpenuhi, UI menampilkan status apa yang kurang.

## Catatan CPU
- Real-ESRGAN/SwinIR/HAT di CPU memang lambat (estimasi jujur ditampilkan di UI).
- Untuk **foto** di CPU: Real-CUGAN (paling cepat) atau Real-ESRGAN (kualitas).
- Untuk **video** di CPU: FSRCNN sangat disarankan.
- Di **GPU** (torch CUDA): semua model AI jauh lebih cepat.

## Struktur
- `app.py` — UI Streamlit
- `enhance.py` — engine (spandrel tiling, FSRCNN, klasik, video + audio mux, batas input)
- `supir.py` — integrasi SUPIR (status + inference)
- `vendor/SUPIR/` — kode resmi SUPIR
- `models/` — bobot model
