# Pak Tukang (Python)
Migrasi dari proyek TypeScript/discord.js ke Python menggunakan discord.py.

## Instalasi
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
```
Isi `.env`, lalu jalankan `python main.py`.

## Fitur yang dipindahkan
- `/bantuan` dengan pilihan Beranda, Utilitas, Automasi
- `/ping`, `/infoserver`, `/infouser`
- `/autothread`, `/daftar-autothread`, `/setup-saran`
- Auto Thread saat pesan baru dan reaksi otomatis
- Panel Kritik & Saran, modal pengiriman, publikasi embed, thread komentar, reaksi
- Penyimpanan konfigurasi JSON

## Catatan migrasi
Versi ini menggunakan Embed + Select Menu sebagai adaptasi tampilan bantuan dan panel saran. Tampilan Discord Components V2 dari discord.js belum direplikasi secara identik di sini. File `data/saran.json` di ZIP asli berisi ID server/channel; nilai tersebut tidak disalin agar konfigurasi dapat diatur ulang dengan `/setup-saran`. Periksa izin bot dan aktifkan Message Content Intent di Developer Portal untuk Auto Thread.
