# ✨ Ampera Enhance (by Ampera Official)

Aplikasi Streamlit untuk memperbesar & meningkatkan kualitas **foto** dan **video**.
Tampilan sederhana dan elegan — latar gelap tenang, tanpa animasi berlebihan.

| Model | Peran | Ukuran | Kecepatan CPU (per tile 256px) |
|---|---|---|---|
| 🥇 **Real-ESRGAN 6B** | **Mesin utama** — animasi & foto | 18 MB | ±11 dtk |
| 🥇 **Real-ESRGAN AnimeVideoV3** | Fidelitas tinggi — super cepat | 2,4 MB | ±1,5 dtk |
| 🥉 **Real-CUGAN** | Mode **Anime** | 5,4 MB | ±4 dtk |
| ⚡ **FSRCNN** | Instan, paling ringan | 40 KB | ±0,05–0,2 dtk |
| 🔧 **Klasik** | Fallback tanpa AI (Lanczos + unsharp) | 0 MB | instan |

> **Real-ESRGAN AnimeVideoV3** (2,4 MB) tidak ikut di repo — aplikasi
> mengunduhnya otomatis saat pertama kali dipakai (tombol *Unduh model*).

## Batas input
- 📷 **Foto maksimal 20 MB**
- 🎬 **Video maksimal 10 detik** (durasi lebih ditolak; audio asli dipertahankan otomatis)
- 🧠 **Anggaran memori**: hasil AI dibatasi ±36 MP (bisa diubah lewat env
  `AMPERA_MAX_OUT_MP`). Foto yang lebih besar otomatis dikecilkan dulu —
  ini mencegah server kehabisan RAM dan mati di tengah proses
  (penyebab umum *"Error running app"* di Streamlit Cloud).

## Fitur
- Pratinjau sebelum/sesudah + unduh (PNG/JPG/MP4)
- Estimasi waktu & jumlah tile ditampilkan **sebelum** proses (diukur dari CPU aktual)
- Tiling 256px dengan cross-fade → bebas sambungan, hemat RAM
- LRU cache model (maks 2 model) agar aman di mesin 2 GB RAM
- Progress bar + ETA per frame untuk video
- Kalau ada model yang belum ada di server (mis. hasil clone parsial), UI otomatis
  menampilkan tombol **⬇️ Unduh model** — user tetap tidak perlu install manual

## Menjalankan

```bash
pip install -r requirements.txt
# torch CPU (tanpa GPU):
pip install torch --index-url https://download.pytorch.org/whl/cpu

streamlit run app.py   # buka http://localhost:8501
```

> Catatan: `streamlit>=1.48` wajib — tombol-tombol memakai parameter
> `width="stretch"` yang baru ada di versi itu. Memakai versi lebih lama
> membuat aplikasi langsung gagal jalan (*Error running app*).

## 📤 Mempublikasikan ke GitHub

**Semua file aman di bawah 25 MB** — upload lewat web GitHub atau `git push`, bebas:

- `app.py`, `enhance.py`, `supir.py`, `download_models.py`
- `requirements.txt`, `README.md`, `.gitignore`
- `models/` — total ±23 MB (file terbesar 18 MB) ✅
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
