# 👷 Pak Tukang --- Bot Discord Kampung Halaman

**Pak Tukang** adalah bot Discord serbaguna (*All-in-One Bot*) berbasis
Python untuk membantu pengelolaan dan aktivitas komunitas **Kampung
Halaman**. Bot menyediakan pusat bantuan, utilitas informasi, serta
automasi Auto Thread dan Kotak Kritik & Saran.

> Status: proyek dasar dengan fitur yang tercantum di bawah. Pastikan
> konfigurasi dan izin bot sudah sesuai sebelum digunakan di server
> produksi.

## Daftar Isi

-   [Fitur](#fitur)
-   [Struktur Proyek](#struktur-proyek)
-   [Teknologi](#teknologi)
-   [Persyaratan](#persyaratan)
-   [Instalasi](#instalasi)
-   [Konfigurasi](#konfigurasi)
-   [Menjalankan Bot](#menjalankan-bot)
-   [Daftar Command](#daftar-command)
-   [Izin dan Intent Discord](#izin-dan-intent-discord)
-   [Penyimpanan Data](#penyimpanan-data)
-   [Pemecahan Masalah](#pemecahan-masalah)
-   [Pengembangan](#pengembangan)

## Fitur

### 🏠 Pusat Bantuan

-   `/bantuan` menampilkan embed bantuan.
-   Menu pilihan kategori **Beranda**, **Utilitas**, dan **Automasi**.
-   Banner Kampung Halaman ditampilkan pada embed.

### 🛠️ Utilitas

-   Memeriksa latensi bot.
-   Menampilkan informasi server Discord.
-   Menampilkan informasi akun pengguna.

### ⚙️ Automasi

-   Mengaktifkan atau menghapus Auto Thread pada channel tertentu.
-   Menampilkan daftar channel yang menggunakan Auto Thread.
-   Menyiapkan panel Kritik & Saran dengan modal.
-   Setiap masukan dikirim ke channel tujuan, dibuatkan thread komentar,
    dan diberi reaksi naik/turun.

## Struktur Proyek

``` text
pak-tukang/
├── main.py
├── requirements.txt
├── .env                  # dibuat sendiri, jangan di-commit
├── bot/
│   ├── __init__.py
│   ├── loader.py
│   ├── store.py
│   └── commands/
│       ├── __init__.py
│       ├── bantuan.py
│       ├── utilitas.py
│       └── automasi.py
└── data/
    ├── autothread.json
    └── saran.json
```

`loader.py` memuat ekstensi command, `store.py` menangani baca/tulis
JSON, sedangkan `main.py` menginisialisasi bot dan melakukan
sinkronisasi slash command.

## Teknologi

-   Python 3.10+ (disarankan menggunakan versi Python yang masih
    didukung).
-   `discord.py` versi 2.6.x.
-   `python-dotenv` untuk membaca variabel lingkungan.

## Persyaratan

-   Python dan pip terpasang.
-   Aplikasi bot dibuat di [Discord Developer
    Portal](https://discord.com/developers/applications).
-   Bot sudah ditambahkan ke server dengan izin yang diperlukan.

## Instalasi

Jalankan perintah dari direktori `pak-tukang/`:

``` bash
# Buat virtual environment
python -m venv .venv

# Aktifkan di Windows PowerShell
.venv\Scripts\Activate.ps1

# Atau di macOS/Linux
source .venv/bin/activate

# Pasang dependensi
python -m pip install -r requirements.txt
```

Jika PowerShell menolak aktivasi, Anda dapat menjalankan pip melalui
interpreter virtual environment secara langsung atau menyesuaikan
Execution Policy untuk sesi tersebut.

## Konfigurasi

Buat file `.env` di direktori yang sama dengan `main.py`:

``` env
DISCORD_TOKEN=isi_token_bot_anda
DISCORD_GUILD_ID=id_server_discord
```

-   `DISCORD_TOKEN`: token rahasia bot dari Developer Portal. Jangan
    bagikan atau unggah ke Git.
-   `DISCORD_GUILD_ID`: ID server untuk sinkronisasi command khusus
    server (guild). Jika dikosongkan atau tidak disetel, bot melakukan
    sinkronisasi global.

Aktifkan **Message Content Intent** pada halaman *Bot* di Developer
Portal karena fitur Auto Thread membaca pesan. Jangan pernah memasukkan
token asli ke README atau repositori publik.

## Menjalankan Bot

Dari direktori `pak-tukang/`, setelah virtual environment aktif dan
`.env` terisi:

``` bash
python main.py
```

Jika berhasil, terminal menampilkan akun bot yang sedang online. Biarkan
proses tetap berjalan agar bot aktif.

## Daftar Command

  ---------------------------------------------------------------------------------
  Command                Kategori          Kegunaan             Akses
  ---------------------- ----------------- -------------------- -------------------
  `/bantuan`             Bantuan           Membuka pusat        Pengguna server
                                           bantuan dan menu     
                                           kategori             

  `/ping`                Utilitas          Memeriksa latensi    Pengguna server
                                           WebSocket bot        

  `/infoserver`          Utilitas          Menampilkan nama,    Pengguna server
                                           ID, pemilik, jumlah  
                                           anggota, dan tanggal 
                                           pembuatan server     

  `/infouser`            Utilitas          Menampilkan          Pengguna server
                                           informasi akun       
                                           pengguna yang        
                                           dipilih atau diri    
                                           sendiri              

  `/autothread`          Automasi          Menambah/menghapus   Memerlukan
                                           Auto Thread pada     `Manage Channels`
                                           channel              

  `/daftar-autothread`   Automasi          Melihat konfigurasi  Memerlukan
                                           Auto Thread          `Manage Channels`

  `/setup-saran`         Automasi          Mengirim panel       Memerlukan
                                           Kritik & Saran ke    `Manage Channels`
                                           channel pilihan      
  ---------------------------------------------------------------------------------

### Cara menggunakan automasi

1.  Jalankan `/autothread` dan pilih aksi tambah atau hapus, lalu
    tentukan channel. Emoji reaksi bersifat opsional dan dipisahkan
    dengan spasi.
2.  Gunakan `/daftar-autothread` untuk memeriksa channel yang terdaftar.
3.  Jalankan `/setup-saran` dan pilih channel tujuan. Bot akan mengirim
    panel dengan tombol **Kirim Saran** dan **Kirim Kritik**.
4.  Anggota menekan tombol, mengisi modal, lalu mengirim masukan. Bot
    memublikasikan masukan dan membuat thread komentar.

## Izin dan Intent Discord

Sesuaikan *OAuth2 URL Generator* saat mengundang bot dan berikan izin
yang relevan, minimal: - View Channels - Send Messages - Embed Links -
Read Message History - Create Public Threads - Send Messages in
Threads - Add Reactions - Manage Threads (jika diperlukan untuk
pengelolaan thread)

Command konfigurasi memakai `default_permissions(manage_channels=True)`.
Hak akses efektif juga dipengaruhi izin server dan konfigurasi Discord.
Aktifkan **Server Members Intent** hanya jika fitur yang ditambahkan
nanti membutuhkannya; kode saat ini mengandalkan intents default
ditambah `guilds`, `guild_messages`, dan `message_content`.

## Penyimpanan Data

Data konfigurasi disimpan secara lokal dalam JSON di folder `data/`: -
`autothread.json`: daftar channel dan pengaturan Auto Thread, termasuk
nama thread dan reaksi. - `saran.json`: pemetaan server ke channel Kotak
Saran.

File akan dibuat otomatis oleh fungsi penyimpanan saat dibaca jika belum
tersedia. Simpan cadangan folder `data/` secara berkala. Jangan
menghapus atau mengedit ID secara manual kecuali memahami dampaknya.

## Pemecahan Masalah

  -----------------------------------------------------------------------
  Gejala                              Pemeriksaan
  ----------------------------------- -----------------------------------
  Bot tidak bisa login                Pastikan `DISCORD_TOKEN` benar,
                                      belum di-reset, dan tidak memiliki
                                      spasi tambahan.

  Slash command tidak muncul          Periksa `DISCORD_GUILD_ID`,
                                      pastikan bot diundang dengan scope
                                      `applications.commands`, lalu cek
                                      log sinkronisasi dan tunggu
                                      propagasi jika memakai sinkronisasi
                                      global.

  Auto Thread tidak berjalan          Pastikan Message Content Intent
                                      aktif di Developer Portal dan izin
                                      baca pesan/channel serta membuat
                                      thread sudah diberikan.

  Panel Saran gagal dikirim           Pastikan channel tujuan berupa
                                      channel teks dan bot memiliki izin
                                      mengirim embed/pesan.

  Reaksi atau thread gagal dibuat     Periksa izin Add Reactions, Create
                                      Public Threads, dan Send Messages
                                      in Threads; periksa juga batasan
                                      channel.

  Data konfigurasi tidak terbaca      Jalankan bot dari direktori
                                      `pak-tukang/` agar folder relatif
                                      `data/` mengarah ke lokasi yang
                                      benar.
  -----------------------------------------------------------------------

## Pengembangan

Command baru dapat ditambahkan sebagai ekstensi di `bot/commands/`, lalu
didaftarkan di daftar ekstensi pada `bot/loader.py`.

Pola umum: 1. Buat class Cog. 2. Definisikan slash command dengan
`app_commands`. 3. Buat fungsi `async def setup(bot)` dan daftarkan Cog
menggunakan `await bot.add_cog(...)`. 4. Tambahkan nama modul ke daftar
ekstensi di `bot/loader.py`. 5. Jalankan ulang bot dan verifikasi
sinkronisasi command.

## Lisensi

Belum ada lisensi yang ditentukan dalam berkas proyek. Tambahkan file
`LICENSE` jika ingin menetapkan ketentuan penggunaan, modifikasi, dan
distribusi.
