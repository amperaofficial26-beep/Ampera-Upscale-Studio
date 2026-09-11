# ✦ Ampera Upscale Studio (by Ampera Official 26)

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

## Halaman

Aplikasi berbentuk multi-halaman dengan **sidebar**:

| Menu | Isi |
|---|---|
| **Home** | Sapaan yang berganti tiap kali dibuka, tombol ajakan mulai, footer |
| **Image Upscale** | Unggah gambar, pratinjau kecil, identitas lengkap + penilaian kualitas, pilihan model |
| **Video Upscale** | Unggah video, pratinjau, identitas lengkap + penilaian kualitas, pilihan model |
| **Gabung ke Ampera** | Profil Ampera Official 26 + paket keanggotaan berbayar |
| **Pelajari Lebih Lanjut** | Cara kerja, daftar model, batasan, tanya jawab |

## Tampilan
- Latar **gradient charcoal & abu-abu yang bergerak** (dua *blob* mengambang pelan),
  otomatis berhenti bila perangkat menyalakan *reduce motion*
- Sidebar kaca (*blur*) dengan menu bergaya navigasi
- Kartu, tabel identitas, dan chip kualitas dengan garis tipis dan aksen tunggal

## Fitur
- **Identitas berkas lengkap** — format, dimensi, megapiksel, rasio aspek, kelas
  resolusi, kanal warna, kedalaman bit, codec, bitrate, frame rate, audio
- **Penilaian kualitas otomatis** — ketajaman (varians Laplacian), derau,
  pencahayaan, kontras, kepadatan data, plus skor 0–100 dan kesimpulan
- Pratinjau sebelum/sesudah + unduh (PNG/JPG/MP4)
- Estimasi waktu & jumlah tile ditampilkan **sebelum** proses
- Tiling 256px dengan cross-fade → bebas sambungan, hemat RAM
- LRU cache model (maks 2 model) agar aman di mesin 2 GB RAM
- Progress bar + ETA per frame untuk video
- Video hasil di-encode **H.264 + faststart** → langsung bisa diputar di browser
- Model yang bobotnya belum ada ditandai *"perlu unduh model"*, dan UI otomatis
  menampilkan tombol **Unduh model**

## Menjalankan

```bash
pip install -r requirements.txt
# torch CPU (tanpa GPU):
pip install torch --index-url https://download.pytorch.org/whl/cpu

streamlit run app.py   # buka http://localhost:8501
```

> Semua bobot model sudah ikut di repo (folder `models/`) — langsung jalan.
> Bila ada yang kurang: `python download_models.py`.

## Struktur

```
app.py          → kerangka: tema, sidebar, router antar halaman
ui.py           → CSS tema (gradient bergerak) + komponen tampilan + format angka
analysis.py     → identitas & penilaian kualitas berkas (foto/video)
presets.py      → katalog model + pemilih model + tombol unduh model
pages_home.py   → halaman Home
pages_image.py  → halaman Image Upscale
pages_video.py  → halaman Video Upscale
pages_join.py   → halaman Gabung ke Ampera (harga masih placeholder)
pages_learn.py  → halaman Pelajari Lebih Lanjut
enhance.py      → engine (spandrel tiling, FSRCNN, klasik, video + audio mux)
download_models.py → unduh model yang hilang
supir.py + vendor/SUPIR/ → integrasi SUPIR (eksperimental, GPU)
models/         → bobot model (semua < 25 MB)
.streamlit/config.toml → tema dasar (dark)
```

> Harga di halaman **Gabung ke Ampera** masih **placeholder** — ubah konstanta
> `PRICE_YEAR`, `PRICE_YEAR_WAS`, `PRICE_MONTH`, `PRICE_LIFETIME` di `pages_join.py`.

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
