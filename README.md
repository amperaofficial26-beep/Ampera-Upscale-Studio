# ✨ Ampera Enhance (by Ampera Official)

Aplikasi Streamlit untuk memperbesar & meningkatkan kualitas **foto** dan **video**.
**Semua model < 25 MB** — bisa di-commit langsung ke GitHub, user tidak perlu
mengunduh apa pun, dan ringan untuk CPU (teman baik dari Streamlit Cloud throttle).

| Model | Peran | Ukuran | Kecepatan CPU (per tile 256px) |
|---|---|---|---|
| 🥇 **Real-ESRGAN 6B** | **Mesin utama** — animasi & foto | 18 MB | ±11 dtk |
| 🥇 **Real-ESRGAN AnimeVideoV3** | **Fidelitas tinggi — super cepat** (pilihan utama video) | 2,4 MB | ±1,5 dtk |
| 🥉 **Real-CUGAN** | Mode **Anime** | 5,4 MB | ±4 dtk |
| ⚡ **FSRCNN** | Instan, paling ringan | 40 KB | ±0,05–0,2 dtk |
| 🔧 **Klasik** | Fallback tanpa AI (Lanczos + unsharp) | 0 MB | instan |

## Batas input
- 📷 **Foto maksimal 20 MB**
- 🎬 **Video maksimal 10 detik** (durasi lebih ditolak; audio asli dipertahankan otomatis)

## Fitur
- UI **elegan & sederhana**: alur linear *Unggah → Pilih kualitas → Proses*
- **Preset** berbasis kebutuhan (Kualitas terbaik / Seimbang / Anime / Cepat / Tanpa AI) —
  nama model teknis disembunyikan di keterangan
- Opsi teknis (pembesaran, ketajaman, batas frame) ada di *Pengaturan lanjutan*
- Pratinjau sebelum/sesudah + unduh (PNG/JPG/MP4)
- Estimasi waktu & jumlah tile ditampilkan **sebelum** proses (diukur dari CPU aktual)
- Tiling 256px dengan cross-fade → bebas sambungan, hemat RAM
- LRU cache model (maks 2 model) agar aman di mesin 2 GB RAM
- Progress bar + ETA per frame untuk video
- Video hasil di-encode **H.264 + faststart** → langsung bisa diputar di browser
- Preset yang bobotnya belum ada ditandai *"perlu unduh model"*, dan UI otomatis
  menampilkan tombol **Unduh model** — user tetap tidak perlu install manual

## Menjalankan

```bash
pip install -r requirements.txt
# torch CPU (tanpa GPU):
pip install torch --index-url https://download.pytorch.org/whl/cpu

streamlit run app.py   # buka http://localhost:8501
```

> Semua bobot model sudah ikut di repo (folder `models/`, total ±26 MB) —
> langsung jalan, tanpa download.

## 📤 Mempublikasikan ke GitHub

**Semua file aman di bawah 25 MB** — upload lewat web GitHub atau `git push`, bebas:

- `app.py`, `enhance.py`, `supir.py`, `download_models.py`
- `requirements.txt`, `README.md`, `.gitignore`
- `models/` — total ±26 MB (file terbesar 18 MB) ✅
- `vendor/SUPIR/` (±29 MB kode, file individual kecil) — boleh ikut / boleh skip

```bash
# contoh alur push dari terminal
git init
git add .
git commit -m "Ampera Enhance — AI upscaler foto & video"
git remote add origin https://github.com/<user>/<repo>.git
git push -u origin main
```

## Model besar (tidak termasuk)
SwinIR (57 MB), HAT (82 MB), Real-ESRGAN x4plus/x2plus (64 MB), dan SUPIR (±8,5 GB)
tidak termasuk karena **tidak memiliki varian resmi di bawah 25 MB**.
Kode engine-nya masih ada di `enhance.py`/`supir.py` dan bisa diaktifkan kembali
bila suatu saat diperlukan — tinggal tambah model-nya ke `SPANDREL_MODELS`.

## 💎 Mode SUPIR (eksperimental, tidak di UI)
Kode terintegrasi di `supir.py` + `vendor/SUPIR/`, aktif hanya bila:
GPU NVIDIA ±11 GB VRAM + xformers + model ±8,5 GB di `models/supir/`.

## Catatan CPU
- Estimasi waktu jujur selalu ditampilkan sebelum proses.
- Untuk **foto**: Real-ESRGAN 6B (kualitas) atau AnimeVideoV3 (cepat).
- Untuk **video**: Real-ESRGAN AnimeVideoV3 (±1,5 dtk/tile) atau FSRCNN (instan).
- Di **GPU** (torch CUDA): semua model jauh lebih cepat.

## Struktur
- `app.py` — UI Streamlit (alur & preset)
- `ui.py` — lapisan tampilan: CSS tema, komponen `brand/label/stats/note`, format angka
- `.streamlit/config.toml` — tema (light, aksen abu-arang)
- `enhance.py` — engine (spandrel tiling, FSRCNN, klasik, video + audio mux, batas input)
- `download_models.py` — unduh model yang hilang (otomatis)
- `supir.py` + `vendor/SUPIR/` — integrasi SUPIR (eksperimental, GPU)
- `models/` — bobot model (semua < 25 MB)
