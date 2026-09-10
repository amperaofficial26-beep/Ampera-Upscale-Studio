"""
Unduh semua bobot model ke folder models/ (yang sudah ada di-skip).

Jalankan:  python download_models.py
"""
import os

import enhance as E


def main():
    os.makedirs(E.MODEL_DIR, exist_ok=True)
    total = len(E.MODEL_DOWNLOADS)
    i = 0
    for fname, (url, size) in E.MODEL_DOWNLOADS.items():
        i += 1
        dest = os.path.join(E.MODEL_DIR, fname)
        if os.path.exists(dest) and os.path.getsize(dest) > 1000:
            print(f"[{i}/{total}] {fname:38s} sudah ada — skip")
            continue
        print(f"[{i}/{total}] {fname:38s} mengunduh ({size / 1024 / 1024:.0f} MB)…")

        def cb(done, tot, fname=fname):
            pct = 100 * done / tot if tot else 0
            print(f"\r    {pct:5.1f}%  ({done / 1024 / 1024:.1f}/{(tot or 0) / 1024 / 1024:.1f} MB)",
                  end="", flush=True)

        E.download_model(fname, progress_cb=cb)
        print(f"    selesai ✅")
    print("\nSemua model siap. Jalankan:  streamlit run app.py")


if __name__ == "__main__":
    main()
