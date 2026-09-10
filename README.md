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

# unduh semua bobot model (yang sudah ada otomatis di-skip)
python download_models.py

streamlit run app.py   # buka http://localhost:8501
```

> **Alternatif tanpa skrip:** jika ada model yang belum ada, app akan menampilkan
> tombol **⬇️ Unduh model** langsung di UI saat engine tersebut dipilih.

## 📤 Mempublikasikan ke GitHub

GitHub membatasi upload web **25 MB per file**, jadi file bobot model yang besar
(RealESRGAN_x4plus 64 MB, SwinIR 57 MB, HAT 82 MB) **tidak boleh di-commit** —
sudah dikecualikan lewat `.gitignore`. Yang perlu di-upload/commit:

- `app.py`, `enhance.py`, `supir.py`, `download_models.py`
- `requirements.txt`, `README.md`, `.gitignore`
- `models/RealCUGAN_up4x.pth` (5,4 MB), `models/RealESRGAN_x4plus_anime_6B.pth` (18 MB),
  `models/FSRCNN_x2/x3/x4.pb` (±40 KB) — kecil, boleh ikut
- `vendor/SUPIR/` (±29 MB kode — boleh, atau skip dan `git clone` di setup)

Setelah itu, pengguna yang meng-clone tinggal jalankan `python download_models.py`
dan semua model besar akan terunduh otomatis.

```bash
# contoh alur push dari terminal
git init
git add .
git commit -m "Ampera Enhance — AI upscaler foto & video"
git remote add origin https://github.com/<user>/<repo>.git
git push -u origin main
```

> Alternatif: **Git LFS** kalau Anda memang ingin bobot model ikut di repo
> (`git lfs track "*.pth" && git lfs install` — butuh akun + kuota LFS 1 GB).

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
