# 👷‍♂️ Pak Tukang — Discord Community Bot

> 🤖 **Pak Tukang** adalah custom Discord Bot berbasis **Python + `discord.py`** yang dirancang sebagai bot serbaguna (*All in One Bot*) untuk membantu mengelola, merawat, dan mengembangkan komunitas Discord **Kampung Halaman**. 🏡

Bot ini dikembangkan secara modular agar fitur dapat dipisahkan ke dalam beberapa *Cog*, mudah dirawat, dan relatif mudah dikembangkan kembali.

---

## 📌 Daftar Isi

- [✨ Tentang Proyek](#-tentang-proyek)
- [🚀 Fitur Utama](#-fitur-utama)
- [🧩 Daftar Slash Command](#-daftar-slash-command)
- [⚙️ Detail Fitur](#️-detail-fitur)
- [🗂️ Struktur Proyek](#️-struktur-proyek)
- [💾 Penyimpanan Data](#-penyimpanan-data)
- [🔐 Permission & Intent](#-permission--intent)
- [🛠️ Teknologi](#️-teknologi)
- [📦 Instalasi](#-instalasi)
- [🔑 Konfigurasi Environment](#-konfigurasi-environment)
- [▶️ Menjalankan Bot](#️-menjalankan-bot)
- [🧱 Arsitektur Singkat](#-arsitektur-singkat)
- [🧪 Perilaku & Penanganan Error](#-perilaku--penanganan-error)
- [🔄 Pengembangan Fitur](#-pengembangan-fitur)
- [⚠️ Catatan Penting](#️-catatan-penting)
- [📄 Lisensi](#-lisensi)

---

## ✨ Tentang Proyek

**Nama:** Pak Tukang  
**Platform:** Discord  
**Bahasa:** Python  
**Library utama:** `discord.py`  
**Target penggunaan:** Community / Server Management  
**Prefix lama:** `!`  
**Interface command saat ini:** `/` (**Slash Commands**)

Pak Tukang menggunakan sistem **Discord Application Commands** sehingga pengguna berinteraksi dengan bot melalui slash command seperti `/bantuan`, `/ping`, dan `/autothread`.

> 💡 **Catatan:** Walaupun instance bot dibuat dengan `command_prefix="!"`, command yang didefinisikan di dalam proyek ini adalah `app_commands`, sehingga penggunaan utamanya tetap melalui `/`.

---

## 🚀 Fitur Utama

### 🏠 Pusat Bantuan
- `/bantuan` menyediakan panel bantuan interaktif.
- Terdapat kategori:
  - 🏠 **Beranda**
  - 🛠️ **Utilitas**
  - ⚙️ **Automasi**
- Navigasi kategori menggunakan **Select Menu**.
- Panel menggunakan **Embed** dan banner server.

### 🛠️ Utilitas
- 🏓 Pemeriksaan latency bot melalui `/ping`.
- 🏡 Informasi server melalui `/infoserver`.
- 👤 Informasi pengguna melalui `/infouser`.

### ⚙️ Automasi
- 🧵 Membuat **Auto Thread** pada channel tertentu.
- 😀 Menambahkan reaksi otomatis pada pesan baru.
- 📋 Melihat daftar channel yang menggunakan Auto Thread.
- 📮 Membuat panel **Kritik & Saran**.
- 💬 Setiap masukan dapat memiliki thread komentar.
- ⬆️⬇️ Postingan masukan otomatis diberi reaksi voting sederhana.

### 💾 Penyimpanan
Konfigurasi automasi disimpan secara lokal menggunakan file **JSON**, sehingga tidak membutuhkan database eksternal.

---

## 🧩 Daftar Slash Command

| Command | Kategori | Fungsi | Akses |
|---|---|---|---|
| `/bantuan` | 🏠 Bantuan | Membuka pusat bantuan interaktif | Semua pengguna |
| `/ping` | 🛠️ Utilitas | Menampilkan latency WebSocket bot | Semua pengguna |
| `/infoserver` | 🛠️ Utilitas | Menampilkan informasi server | Semua pengguna |
| `/infouser` | 🛠️ Utilitas | Menampilkan informasi pengguna Discord | Semua pengguna |
| `/autothread` | ⚙️ Automasi | Menambah atau menghapus Auto Thread | `Manage Channels` |
| `/daftar-autothread` | ⚙️ Automasi | Menampilkan konfigurasi Auto Thread | `Manage Channels` |
| `/setup-saran` | ⚙️ Automasi | Membuat panel Kritik & Saran | `Manage Channels` |

> 🔒 Command automasi menggunakan `default_permissions(manage_channels=True)`, sehingga Discord membatasi command tersebut kepada pengguna yang memiliki permission **Manage Channels**.

---

## ⚙️ Detail Fitur

### 🏓 `/ping`

Memeriksa latency WebSocket bot.

Contoh respons:

```text
🏓 Pong!
WebSocket: 42 ms
```

Nilai latency dihitung dari `bot.latency` dan ditampilkan dalam milidetik (`ms`).

---

### 🏡 `/infoserver`

Menampilkan informasi dasar server Discord tempat command dijalankan:

- Nama server
- Server ID
- Pemilik server
- Jumlah anggota
- Tanggal pembuatan server

Command ini hanya dapat digunakan di dalam server/guild.

---

### 👤 `/infouser`

Menampilkan informasi pengguna Discord.

Jika parameter `pengguna` tidak diberikan, bot akan menampilkan informasi pengguna yang menjalankan command.

Informasi yang ditampilkan:

- Username
- User ID
- Status apakah akun merupakan bot
- Tanggal pembuatan akun
- Tanggal bergabung ke server, apabila pengguna merupakan member server

---

### 🧵 `/autothread`

Digunakan untuk mengaktifkan atau menonaktifkan Auto Thread pada sebuah **Text Channel**.

Parameter:

| Parameter | Tipe | Keterangan |
|---|---|---|
| `aksi` | Choice | `Menambahkan (Add)` atau `Menghapus (Remove)` |
| `channel` | Text Channel | Channel target |
| `reaksi` | String | Emoji dipisahkan menggunakan spasi |

#### ➕ Menambahkan Auto Thread

Saat channel didaftarkan:

1. Konfigurasi channel disimpan ke `data/autothread.json`.
2. Nama thread default ditetapkan.
3. Daftar emoji reaksi disimpan.
4. Bot memberikan konfirmasi secara ephemeral.

Contoh konsep penggunaan:

```text
/autothread
aksi: Menambahkan (Add)
channel: #diskusi
reaksi: 🔥 👍
```

Setelah aktif, pesan baru dari pengguna di channel tersebut akan diproses oleh listener Auto Thread.

#### ➖ Menghapus Auto Thread

Dengan aksi `Menghapus (Remove)`, konfigurasi channel akan dihapus dari penyimpanan JSON.

Bot juga menampilkan daftar channel yang sebelumnya terdaftar sebelum mengonfirmasi penghapusan.

---

### 🧵 Auto Thread Listener

Fitur Auto Thread berjalan melalui event:

```python
on_message
```

Bot akan mengabaikan:

- Pesan yang bukan berasal dari guild.
- Pesan dari bot lain.
- Pesan pada channel yang bukan `TextChannel`.
- Channel yang tidak terdaftar sebagai Auto Thread.

Untuk pesan yang memenuhi kondisi:

1. Bot membuat thread baru.
2. Nama thread menggunakan konfigurasi `threadName`.
3. Thread menggunakan `auto_archive_duration=1440`.
4. Bot mencoba menambahkan seluruh emoji yang tersimpan pada konfigurasi channel.

> ℹ️ `1440` menit = **24 jam**.

---

### 📋 `/daftar-autothread`

Menampilkan seluruh channel yang saat ini tersimpan dalam konfigurasi Auto Thread.

Setiap entry menampilkan:

- Nomor konfigurasi
- Channel
- Nama thread
- Daftar reaksi otomatis

Jika channel sudah tidak dapat ditemukan oleh bot, konfigurasi tetap ditampilkan menggunakan format `<#CHANNEL_ID>` dan diberi keterangan bahwa channel tidak ditemukan.

---

### 📮 `/setup-saran`

Membuat panel **Kotak Saran & Kritik** pada channel yang dipilih.

Panel menyediakan dua tombol:

| Tombol | Fungsi |
|---|---|
| 💡 **Kirim Saran** | Membuka formulir untuk mengirim saran |
| 🗣️ **Kirim Kritik** | Membuka formulir untuk mengirim kritik |

Konfigurasi channel disimpan berdasarkan:

- `guildId`
- `channelId`

Jika server sebelumnya sudah memiliki konfigurasi Kotak Saran, konfigurasi lama akan digantikan oleh konfigurasi baru.

---

### 💡 Alur Kritik & Saran

Alur fitur:

```text
👤 Pengguna
    │
    ▼
📮 Panel Kritik & Saran
    │
    ├── 💡 Kirim Saran
    │
    └── 🗣️ Kirim Kritik
             │
             ▼
        📝 Modal Form
             │
             ▼
      📤 Kirim Masukan
             │
             ▼
      📌 Embed Publik
             │
       ┌─────┴─────┐
       ▼           ▼
     ⬆️ Reaksi    ⬇️ Reaksi
       │
       ▼
    💬 Thread Komentar
```

Setelah formulir dikirim:

1. Bot mencari channel Kotak Saran yang dikonfigurasi untuk guild.
2. Isi masukan diformat sebagai blockquote.
3. Bot mengirim masukan sebagai Embed.
4. Bot membuat thread komentar pada postingan.
5. Bot menambahkan reaksi `⬆️` dan `⬇️`.
6. Pengirim menerima respons ephemeral berisi link postingan dan thread komentar.

---

## 🗂️ Struktur Proyek

```text
bot-discord-kampung-halaman-paktukang-python-main/
│
├── .gitignore
│
└── pak-tukang/
    │
    ├── README.md
    ├── requirements.txt
    ├── main.py
    │
    ├── bot/
    │   ├── __init__.py
    │   ├── loader.py
    │   ├── store.py
    │   │
    │   └── commands/
    │       ├── __init__.py
    │       ├── bantuan.py
    │       ├── utilitas.py
    │       └── automasi.py
    │
    └── data/
        ├── autothread.json
        └── saran.json
```

### 📄 Penjelasan File

#### `main.py`
Entry point aplikasi.

Tugas utamanya:

- Memuat environment variable.
- Membuat Discord intents.
- Membuat instance `PakTukang`.
- Memuat seluruh extension/Cog.
- Melakukan sinkronisasi slash command.
- Menjalankan bot menggunakan token.

#### `bot/loader.py`
Menjadi extension loader.

Extension yang dimuat:

```text
bot.commands.bantuan
bot.commands.utilitas
bot.commands.automasi
```

Dengan pendekatan ini, setiap kelompok fitur dapat dikembangkan secara terpisah.

#### `bot/store.py`
Menangani penyimpanan JSON lokal.

Fungsi utama:

- `read()` → membaca data JSON.
- `write()` → menulis data JSON.

Folder `data/` akan dibuat otomatis apabila belum tersedia.

#### `bot/commands/bantuan.py`
Berisi:

- `/bantuan`
- `HelpSelect`
- `HelpView`
- Embed bantuan berdasarkan kategori.

#### `bot/commands/utilitas.py`
Berisi:

- `/ping`
- `/infoserver`
- `/infouser`

#### `bot/commands/automasi.py`
Berisi fitur automasi terbesar:

- `/autothread`
- `/daftar-autothread`
- `/setup-saran`
- `SaranModal`
- `SaranView`
- Listener `on_message`
- Persistent View untuk tombol Kritik & Saran

---

## 💾 Penyimpanan Data

Pak Tukang menggunakan **JSON storage**, bukan database SQL/NoSQL.

### `data/autothread.json`

Menyimpan konfigurasi Auto Thread.

Format datanya berupa array object:

```json
[
  {
    "channelId": "123456789012345678",
    "threadName": "Diskusi",
    "reactions": ["🔥", "👍"]
  }
]
```

Field:

| Field | Fungsi |
|---|---|
| `channelId` | ID channel target |
| `threadName` | Nama thread yang dibuat |
| `reactions` | Daftar emoji otomatis |

---

### `data/saran.json`

Menyimpan channel Kotak Saran berdasarkan server.

Format:

```json
[
  {
    "guildId": "123456789012345678",
    "channelId": "987654321098765432"
  }
]
```

Field:

| Field | Fungsi |
|---|---|
| `guildId` | ID server Discord |
| `channelId` | ID channel Kotak Saran |

> 🔐 File JSON dapat berisi ID Discord yang spesifik terhadap server. Hindari membagikan konfigurasi produksi apabila repository akan dibuat publik.

---

## 🔐 Permission & Intent

### Discord Intents

Bot mengaktifkan:

```python
intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.message_content = True
```

### ⚠️ Message Content Intent

Fitur Auto Thread menggunakan `on_message` dan membaca event pesan. Karena itu, **Message Content Intent** perlu diperhatikan pada konfigurasi bot Discord.

Pastikan intent yang diperlukan diaktifkan pada **Discord Developer Portal** dan konfigurasi kode tetap sesuai kebutuhan bot.

### 🔒 Permission Command

Command berikut membutuhkan permission:

```text
Manage Channels
```

- `/autothread`
- `/daftar-autothread`
- `/setup-saran`

Selain pembatasan command melalui `default_permissions`, bot tetap membutuhkan permission Discord yang sesuai agar dapat membuat thread, mengirim pesan, menambahkan reaksi, dan menggunakan fitur komponen.

---

## 🛠️ Teknologi

| Teknologi | Peran |
|---|---|
| 🐍 **Python** | Bahasa pemrograman |
| 🤖 **discord.py** | Framework/library Discord API |
| 🔐 **python-dotenv** | Memuat konfigurasi dari `.env` |
| 📦 **JSON** | Penyimpanan konfigurasi lokal |
| ⚡ **Discord Application Commands** | Sistem Slash Command |
| 🧩 **Discord Cogs/Extensions** | Modularisasi fitur |

Versi dependency utama:

```text
discord.py >= 2.6, < 3.0
python-dotenv >= 1.0, < 2.0
```

---

## 📦 Instalasi

### 1. Clone / Extract Repository

Masuk ke folder proyek:

```bash
cd pak-tukang
```

### 2. Buat Virtual Environment

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

#### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependency

```bash
pip install -r requirements.txt
```

---

## 🔑 Konfigurasi Environment

Buat file:

```text
.env
```

Contoh:

```env
DISCORD_TOKEN=TOKEN_BOT_DISCORD_KAMU
DISCORD_GUILD_ID=ID_SERVER_DISCORD
```

### `DISCORD_TOKEN`

Token autentikasi bot Discord.

> 🚨 **JANGAN PERNAH** memasukkan token bot ke repository publik, screenshot, README, atau membagikannya kepada orang lain.

### `DISCORD_GUILD_ID`

ID server/guild yang digunakan untuk sinkronisasi command.

Jika variable ini tersedia, bot melakukan sinkronisasi command ke guild tersebut:

```python
self.tree.copy_global_to(guild=guild)
await self.tree.sync(guild=guild)
```

Jika tidak tersedia, bot melakukan global sync:

```python
await self.tree.sync()
```

> 💡 Untuk pengembangan, sinkronisasi ke guild tertentu biasanya lebih praktis karena perubahan command dapat diuji pada server target tanpa bergantung pada sinkronisasi global.

---

## ▶️ Menjalankan Bot

Setelah `.env` dan dependency siap:

```bash
python main.py
```

Jika berhasil, terminal akan menampilkan:

```text
Pak Tukang online sebagai ...
```

Bot kemudian siap menerima slash command yang telah tersinkronisasi.

---

## 🧱 Arsitektur Singkat

Secara sederhana, alur aplikasi adalah:

```text
                    ┌───────────────────┐
                    │     main.py       │
                    │   Bot Entrypoint  │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │     loader.py     │
                    │ Load Extensions   │
                    └─────────┬─────────┘
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
      ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
      │   bantuan   │  │   utilitas  │  │  automasi   │
      │     Cog     │  │     Cog     │  │     Cog     │
      └─────────────┘  └─────────────┘  └──────┬──────┘
                                               │
                                               ▼
                                      ┌─────────────────┐
                                      │    store.py     │
                                      │   JSON Storage  │
                                      └────────┬────────┘
                                               │
                              ┌────────────────┴───────────────┐
                              ▼                                ▼
                       autothread.json                    saran.json
```

Pendekatan ini membuat kode lebih terorganisir karena:

- `main.py` fokus pada lifecycle bot.
- `loader.py` fokus pada pemuatan module.
- Setiap Cog menangani domain fitur masing-masing.
- `store.py` menangani persistence.
- `data/` menyimpan konfigurasi.

---

## 🧪 Perilaku & Penanganan Error

Beberapa validasi telah diterapkan di dalam bot.

### 🧵 Auto Thread

Bot tidak akan membuat thread jika:

- Pesan berasal dari bot.
- Pesan bukan berasal dari guild.
- Channel bukan `TextChannel`.
- Channel tidak terdaftar pada konfigurasi Auto Thread.

Jika Discord API menolak pembuatan thread atau penambahan reaksi, exception `discord.HTTPException` ditangani dan error dicetak ke console.

### 📮 Kritik & Saran

Bot memeriksa:

- Apakah guild memiliki konfigurasi Kotak Saran.
- Apakah channel yang tersimpan masih dapat ditemukan.
- Apakah channel merupakan `TextChannel`.

Jika konfigurasi belum tersedia, pengguna menerima pesan:

```text
❌ Kotak Saran belum diatur oleh staf.
```

---

## 🔄 Pengembangan Fitur

Untuk menambahkan fitur baru, pola yang direkomendasikan adalah membuat atau memperluas **Cog**.

Contoh:

```text
bot/
└── commands/
    ├── bantuan.py
    ├── utilitas.py
    ├── automasi.py
    └── fitur_baru.py
```

Kemudian daftarkan extension pada:

```text
bot/loader.py
```

Contoh:

```python
async def load_extensions(bot):
    for name in [
        "bot.commands.bantuan",
        "bot.commands.utilitas",
        "bot.commands.automasi",
        "bot.commands.fitur_baru"
    ]:
        await bot.load_extension(name)
```

### 💡 Rekomendasi Pengembangan Berikutnya

Beberapa arah pengembangan yang kompatibel dengan arsitektur saat ini:

- 🗄️ Migrasi JSON → SQLite/PostgreSQL untuk skala lebih besar.
- 🧾 Sistem logging yang lebih terstruktur.
- 🛡️ Permission/role management yang lebih granular.
- 📊 Statistik penggunaan command.
- 🔔 Sistem notifikasi moderasi.
- ⚙️ Dashboard konfigurasi.
- 🌐 Konfigurasi per-guild yang lebih lengkap.
- 🧪 Automated testing untuk fungsi storage dan command logic.
- 📝 Logging error ke channel khusus administrator.

---

## ⚠️ Catatan Penting

### 🔐 Jangan Commit `.env`

File `.gitignore` sudah menyediakan aturan untuk mengecualikan `.env` dan virtual environment:

```gitignore
.env
.env.*
!.env.example

__pycache__/
*.py[cod]
.venv/
```

### 🪪 ID Discord

`guildId` dan `channelId` bukan secret seperti token, tetapi tetap merupakan data konfigurasi spesifik server. Pertimbangkan untuk tidak menyertakan konfigurasi produksi dalam repository publik.

### 📡 Discord API

Beberapa fitur bergantung pada permission dan kondisi Discord API, terutama:

- Membuat thread
- Menambahkan reaction
- Mengirim message/embed
- Menggunakan interaction/component
- Mengakses informasi guild/member

Jika fitur tertentu gagal, periksa permission bot pada channel/server terlebih dahulu.

### 💾 JSON Storage

Penyimpanan JSON cocok untuk proyek kecil hingga menengah dan konfigurasi sederhana. Untuk deployment multi-instance atau kebutuhan data yang lebih kompleks, database akan lebih tepat.

---

## 📄 Lisensi

Proyek ini sudah memiliki file **`LICENSE`** pada repository.

Untuk mengetahui ketentuan penggunaan, penyalinan, modifikasi, dan distribusi proyek secara lengkap, silakan merujuk langsung ke:

```text
LICENSE
```

> ⚖️ **Catatan:** Ketentuan yang berlaku adalah ketentuan yang tercantum di dalam file `LICENSE` pada repository ini.

---

## 👷‍♂️ Tentang Pak Tukang

**Pak Tukang** dibuat sebagai bot custom untuk ekosistem komunitas **Kampung Halaman**.

Konsepnya sederhana:

> 🛠️ **Membangun, merawat, dan membantu mengembangkan server Discord melalui automasi.**

Bot ini dikembangkan dengan pendekatan modular agar fitur dapat terus ditambahkan tanpa membuat seluruh project menjadi satu file besar.

---

<div align="center">

### 🏡 Kampung Halaman × 👷‍♂️ Pak Tukang

**Custom Discord Bot • Python • discord.py**

_Keep building. Keep improving. Keep the community alive. 🛠️_

</div>
