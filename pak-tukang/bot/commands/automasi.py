import discord
from discord import app_commands
from discord.ext import commands

BANNER_URL= "https://cdn.discordapp.com/attachments/1545650023793041439/1553221942981558312/banner-server-discord-Kampung-Halaman-Garis.png?ex=6abb1928&is=6ab9c7a8&hm=3c2352b28839311353fab815a8f03d7f4cbbd078e86868ff24c72d17b7873531"

from bot.store import read, write
from datetime import datetime, timezone
from urllib.parse import urlparse
import uuid


DEFAULT = "💬 Kolom Komentar"


def configs():
    return read("autothread.json", [])


def saran():
    return read("saran.json", [])


# =========================================================
# MODAL KRITIK & SARAN
# =========================================================

class SaranModal(discord.ui.Modal):
    isi = discord.ui.TextInput(
        label="Masukkan Kritik/Saran di bawah ini.",
        style=discord.TextStyle.paragraph,
        placeholder="Tuliskan ide, kritik, atau saran kamu...",
        max_length=4000,
        required=True
    )

    def __init__(self, jenis: str):
        self.jenis = jenis
        super().__init__(title=f"📝 Kirim {jenis}")

    async def on_submit(self, i: discord.Interaction):
        value = self.isi.value.strip()

        if not value:
            return await i.response.send_message(
                "❌ Kritik atau Saran tidak boleh kosong.",
                ephemeral=True
            )

        cfg = next(
            (
                x for x in saran()
                if x.get("guildId") == str(i.guild_id)
            ),
            None
        )

        if not cfg:
            return await i.response.send_message(
                "❌ Kotak Saran belum diatur oleh staf.",
                ephemeral=True
            )

        if not i.guild:
            return await i.response.send_message(
                "❌ Perintah ini hanya dapat digunakan di server.",
                ephemeral=True
            )

        ch = i.guild.get_channel(int(cfg["channelId"]))

        if not isinstance(ch, discord.TextChannel):
            return await i.response.send_message(
                "❌ Channel Kotak Saran tidak ditemukan.",
                ephemeral=True
            )

        emoji = "💡" if self.jenis == "Saran" else "🗣️"

        # Format setiap baris pesan dengan blockquote dan panah kanan
        isi_berformat = "\\n".join(
            f"> {baris}" for baris in value.splitlines()
        )

        # Tetapkan nama tipe dan emoji secara eksplisit.
        tipe_emoji = {
            "Saran": "💡",
            "Kritik": "🗣️"
        }
        emoji_tipe = tipe_emoji.get(self.jenis, "📝")

        # Embed masukan: Pengirim dan Tipe sejajar, deskripsi di bawah.
        e = discord.Embed(
            title=f"{emoji_tipe} {self.jenis} Baru",
            color=0xffffff,
            timestamp=discord.utils.utcnow()
        )
        e.add_field(
            name="👤 Pengirim",
            value=i.user.mention,
            inline=True
        )
        e.add_field(
            name="🏷️ Tipe",
            value=f"{emoji_tipe} {self.jenis}",
            inline=True
        )
        e.add_field(
            name="​",
            value=isi_berformat,
            inline=False
        )

        e.set_author(
            name=i.user.name,
            icon_url=i.user.display_avatar.url
        )

        e.set_footer(
            text="Kampung Halaman | Kotak Saran"
        )

        # Setiap masukan memiliki dua tombol seperti panel awal
        post = await ch.send(
            embed=e,
            view=SaranView()
        )

        # Buat kolom komentar
        thread = await post.create_thread(
            name=DEFAULT,
            auto_archive_duration=1440,
            reason="Kolom komentar Kritik & Saran"
        )

        # Reaksi pada postingan
        for emoji_reaction in ("⬆️", "⬇️"):
            try:
                await post.add_reaction(emoji_reaction)
            except discord.HTTPException as ex:
                print(
                    f"Gagal menambahkan reaksi "
                    f"{emoji_reaction}: {ex}"
                )

        await i.response.send_message(
            f"✅ **{self.jenis} berhasil dikirim!**\n"
            f"📨 Postingan: {post.jump_url}\n"
            f"💬 Kolom Komentar: {thread.mention}",
            ephemeral=True
        )


# =========================================================
# VIEW TOMBOL KRITIK & SARAN
# =========================================================

class SaranView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Kirim Saran",
        emoji="💡",
        style=discord.ButtonStyle.primary,
        custom_id="saran:open:saran"
    )
    async def open_saran(
        self,
        i: discord.Interaction,
        button: discord.ui.Button
    ):
        await i.response.send_modal(
            SaranModal("Saran")
        )

    @discord.ui.button(
        label="Kirim Kritik",
        emoji="🗣️",
        style=discord.ButtonStyle.secondary,
        custom_id="saran:open:kritik"
    )
    async def open_kritik(
        self,
        i: discord.Interaction,
        button: discord.ui.Button
    ):
        await i.response.send_modal(
            SaranModal("Kritik")
        )



# =========================================================
# MUTUALAN MEDIA SOSIAL
# =========================================================

SOCIAL_FIELDS = [
    ("instagram", "Instagram", "<:kh_instagram:1546673046746562602>", "https://instagram.com/username"),
    ("tiktok", "TikTok", "<:kh_tiktok:1546673122525188196>", "https://tiktok.com/@username"),
    ("facebook", "Facebook", "<:kh_facebook:1554520636716490832>", "https://facebook.com/username"),
    ("x", "X", "<:kh_x:1546673178003116062>", "https://x.com/username"),
    ("whatsapp", "Saluran WhatsApp", "<:kh_whatsapp:1546673322018738226>", "https://whatsapp.com/channel/..."),
]


def mutual_profiles():
    return read("mutual_medsos.json", [])


def save_mutual_profiles(data):
    write("mutual_medsos.json", data)


def mutual_settings():
    return read("mutual_medsos_settings.json", [])


def save_mutual_settings(data):
    write("mutual_medsos_settings.json", data)


def valid_social_url(value):
    if not value:
        return True
    parsed = urlparse(value)
    return (
        parsed.scheme in ("http", "https")
        and bool(parsed.netloc)
        and "." in parsed.netloc
    )


def mutual_embed(profile, user=None):
    embed = discord.Embed(
        description=(
            "# 📲 Mutualan Media Sosial\n"
            "Berikut media sosial "
            f"<@{profile['user_id']}> yang bisa kamu kunjungi."
        ),
        color=discord.Color.from_rgb(255, 255, 255),
    )
    # Nama user tetap ditampilkan sebagai author, sementara avatar user
    # ditempatkan di sisi kanan embed melalui thumbnail Discord.
    avatar_url = profile.get("avatar_url") or None
    embed.set_author(
        name=profile.get("display_name", "Warga Kampung Halaman"),
    )
    if avatar_url:
        embed.set_thumbnail(url=avatar_url)

    # Banner server ditampilkan di bagian bawah profil mutualan.
    if BANNER_URL:
        embed.set_image(url=BANNER_URL)

    embed.set_footer(text="🏡 Kampung Halaman | Mutualan Media Sosial")
    return embed


class MutualUploadFirstModal(discord.ui.Modal):
    def __init__(self, cog, mode, existing=None):
        super().__init__(
            title="Upload Media Sosial" if mode == "upload" else "Edit Media Sosial"
        )
        self.cog = cog
        self.mode = mode
        self.existing = existing or {}
        self.inputs = {}

        # Discord Modal maksimal memiliki 5 komponen TextInput.
        # Lima platform ini karena Threads sudah dihapus.
        for key, label, emoji, placeholder in SOCIAL_FIELDS:
            field = discord.ui.TextInput(
                label=label,
                placeholder=placeholder,
                default=self.existing.get(key, "") or None,
                required=False,
                max_length=300,
            )
            self.inputs[key] = field
            self.add_item(field)

    async def on_submit(self, interaction: discord.Interaction):
        values = {
            key: (field.value or "").strip()
            for key, field in self.inputs.items()
        }

        invalid = [
            label
            for key, label, _, _ in SOCIAL_FIELDS
            if values.get(key) and not valid_social_url(values[key])
        ]
        if invalid:
            return await interaction.response.send_message(
                "❌ URL tidak valid untuk: "
                + ", ".join(invalid)
                + ". Gunakan tautan lengkap yang diawali http:// atau https://.",
                ephemeral=True,
            )

        # Langsung simpan. Tidak ada langkah kedua / modal Threads.
        await self.cog.save_mutual_profile(interaction, values)


class MutualPanelView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(
        label="Upload",
        emoji="📤",
        style=discord.ButtonStyle.primary,
        custom_id="mutual:upload",
    )
    async def upload(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(
            MutualUploadFirstModal(self.cog, "upload")
        )


class MutualProfileView(discord.ui.View):
    def __init__(self, cog, profile):
        super().__init__(timeout=None)
        self.cog = cog
        self.profile_id = profile["id"]

        # Link tombol hanya dibuat untuk platform yang memiliki URL.
        for key, label, emoji, _ in SOCIAL_FIELDS:
            url = (profile.get(key) or "").strip()
            if url:
                self.add_item(discord.ui.Button(
                    label=label,
                    emoji=emoji,
                    style=discord.ButtonStyle.link,
                    url=url,
                ))

        edit_button = discord.ui.Button(
            label="Edit",
            emoji="✏️",
            style=discord.ButtonStyle.secondary,
            custom_id=f"mutual:profile-edit:{self.profile_id}",
        )
        edit_button.callback = self.edit_profile
        self.add_item(edit_button)

        delete_button = discord.ui.Button(
            label="Hapus",
            emoji="🗑️",
            style=discord.ButtonStyle.danger,
            custom_id=f"mutual:profile-delete:{self.profile_id}",
        )
        delete_button.callback = self.delete_profile
        self.add_item(delete_button)

        upload_button = discord.ui.Button(
            label="Upload",
            emoji="📤",
            style=discord.ButtonStyle.primary,
            custom_id=f"mutual:profile-upload:{self.profile_id}",
        )
        upload_button.callback = self.upload_profile
        self.add_item(upload_button)

    def get_profile(self):
        return next(
            (
                item for item in mutual_profiles()
                if item.get("id") == self.profile_id
            ),
            None,
        )

    async def edit_profile(self, interaction: discord.Interaction):
        profile = self.get_profile()
        if not profile:
            return await interaction.response.send_message(
                "Profil tidak ditemukan.", ephemeral=True
            )

        if profile.get("user_id") != str(interaction.user.id):
            return await interaction.response.send_message(
                "Kamu hanya dapat mengedit profil milikmu sendiri.",
                ephemeral=True,
            )

        await interaction.response.send_modal(
            MutualUploadFirstModal(self.cog, "edit", profile)
        )

    async def upload_profile(self, interaction: discord.Interaction):
        profile = self.get_profile()
        if not profile:
            return await interaction.response.send_message(
                "Profil tidak ditemukan.", ephemeral=True
            )

        if profile.get("user_id") != str(interaction.user.id):
            return await interaction.response.send_message(
                "Kamu hanya dapat mengunggah ulang profil milikmu sendiri.",
                ephemeral=True,
            )

        # Upload dari profil membuka satu form yang sama dan langsung menyimpan.
        await interaction.response.send_modal(
            MutualUploadFirstModal(self.cog, "upload", profile)
        )

    async def delete_profile(self, interaction: discord.Interaction):
        profile = self.get_profile()
        if not profile:
            return await interaction.response.send_message(
                "Profil tidak ditemukan.", ephemeral=True
            )

        if profile.get("user_id") != str(interaction.user.id):
            return await interaction.response.send_message(
                "Kamu hanya dapat menghapus profil milikmu sendiri.",
                ephemeral=True,
            )

        # Hapus data profil dari penyimpanan terlebih dahulu.
        data = [
            item for item in mutual_profiles()
            if item.get("id") != self.profile_id
        ]
        save_mutual_profiles(data)

        # Hapus thread komentar jika masih ada.
        if interaction.guild and profile.get("thread_id"):
            try:
                thread = interaction.guild.get_thread(int(profile["thread_id"]))
                if thread is None and interaction.message:
                    channel = interaction.message.channel
                    if isinstance(channel, discord.TextChannel):
                        thread = channel.get_thread(int(profile["thread_id"]))
                if thread:
                    await thread.delete(reason="Profil Mutualan Media Sosial dihapus")
            except (discord.NotFound, discord.Forbidden, discord.HTTPException, ValueError):
                pass

        # Hapus pesan profil.
        try:
            if interaction.message:
                await interaction.message.delete()
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            return await interaction.response.send_message(
                "✅ Data profil sudah dihapus, tetapi pesan profil tidak dapat dihapus oleh bot.",
                ephemeral=True,
            )

        await interaction.response.send_message(
            "✅ Profil Mutualan Media Sosial berhasil dihapus.",
            ephemeral=True,
        )


# =========================================================
# COG AUTOMASI
# =========================================================

class Automasi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =====================================================
    # AUTOTHREAD
    # =====================================================

    @app_commands.command(
        name="autothread",
        description="Tambah atau hapus Auto Thread"
    )
    @app_commands.default_permissions(
        manage_channels=True
    )
    @app_commands.describe(
        aksi="Pilih tindakan",
        channel="Channel teks",
        reaksi="Emoji dipisahkan spasi"
    )
    @app_commands.choices(
        aksi=[
            app_commands.Choice(
                name="Menambahkan (Add)",
                value="tambah"
            ),
            app_commands.Choice(
                name="Menghapus (Remove)",
                value="hapus"
            )
        ]
    )
    async def autothread(
        self,
        i: discord.Interaction,
        aksi: app_commands.Choice[str],
        channel: discord.TextChannel,
        reaksi: str = ""
    ):
        data = configs()

        old = next(
            (
                x for x in data
                if x.get("channelId") == str(channel.id)
            ),
            None
        )

        # TAMBAH AUTOTHREAD
        if aksi.value == "tambah":
            if old:
                return await i.response.send_message(
                    "⚠️ Channel tersebut sudah menggunakan "
                    "Auto Thread.",
                    ephemeral=True
                )

            reactions = reaksi.split()

            data.append({
                "channelId": str(channel.id),
                "threadName": DEFAULT,
                "reactions": reactions
            })

            write("autothread.json", data)

            return await i.response.send_message(
                "✅ **Auto Thread berhasil ditambahkan!**\n\n"
                f"**Channel:** {channel.mention}\n"
                f"**Nama Thread:** {DEFAULT}\n"
                f"**Auto Reaction:** "
                f"{' '.join(reactions) or 'Tidak ada'}",
                ephemeral=True
            )

        # HAPUS AUTOTHREAD
        if not old:
            return await i.response.send_message(
                "⚠️ Channel tersebut belum terdaftar "
                "di Auto Thread.",
                ephemeral=True
            )

        # Ambil daftar channel sebelum penghapusan
        aktif = []

        for item in data:
            channel_id = item.get("channelId")

            if not channel_id:
                continue

            ch = (
                i.guild.get_channel(int(channel_id))
                if i.guild
                else None
            )

            if ch:
                aktif.append(ch.mention)
            else:
                aktif.append(f"<#{channel_id}>")

        # Hapus konfigurasi channel yang dipilih
        data = [
            x for x in data
            if x.get("channelId") != str(channel.id)
        ]

        write("autothread.json", data)

        daftar = (
            "\n".join(f"• {mention}" for mention in aktif)
            if aktif
            else "Tidak ada channel aktif."
        )

        await i.response.send_message(
            "**📋 Channel yang menggunakan Auto Thread "
            "sebelum penghapusan:**\n"
            f"{daftar}\n\n"
            f"✅ Auto Thread berhasil dihapus dari "
            f"{channel.mention}.",
            ephemeral=True
        )

    # =====================================================
    # DAFTAR AUTOTHREAD
    # =====================================================

    @app_commands.command(
        name="daftar-autothread",
        description="Menampilkan daftar channel Auto Thread"
    )
    @app_commands.default_permissions(
        manage_channels=True
    )
    async def daftar(self, i: discord.Interaction):
        rows = []

        for n, x in enumerate(configs(), 1):
            channel_id = x.get("channelId")

            if not channel_id:
                continue

            ch = (
                i.guild.get_channel(int(channel_id))
                if i.guild
                else None
            )

            if ch:
                rows.append(
                    f"**{n}.** {ch.mention}\n"
                    f"> Nama Thread: "
                    f"{x.get('threadName', DEFAULT)}\n"
                    f"> Auto Reaction: "
                    f"{' '.join(x.get('reactions', [])) or 'Tidak ada'}"
                )
            else:
                rows.append(
                    f"**{n}.** <#{channel_id}> "
                    "(Channel tidak ditemukan)\n"
                    f"> Nama Thread: "
                    f"{x.get('threadName', DEFAULT)}\n"
                    f"> Auto Reaction: "
                    f"{' '.join(x.get('reactions', [])) or 'Tidak ada'}"
                )

        if rows:
            description = (
                "**📋 Daftar Auto Thread**\n\n"
                + "\n\n".join(rows)
            )
        else:
            description = (
                "Belum ada channel yang menggunakan "
                "Auto Thread."
            )

        await i.response.send_message(
            description,
            ephemeral=True
        )

    # =====================================================
    # SETUP SARAN
    # =====================================================

    @app_commands.command(
        name="setup-saran",
        description="Mengatur channel khusus Kritik & Saran"
    )
    @app_commands.default_permissions(
        manage_channels=True
    )
    @app_commands.describe(
        channel="Channel untuk Kotak Saran"
    )
    async def setup_saran(
        self,
        i: discord.Interaction,
        channel: discord.TextChannel
    ):
        e = discord.Embed(
            description=(
                "# 📮 Kotak Saran & Kritik\n"
                "Punya ide, kritik, atau saran untuk "
                "Kampung Halaman? Sampaikan melalui "
                "formulir di bawah ini. Setiap masukan "
                "membantu warga membangun komunitas bersama.\n\n"
                "**Pilih tombol sesuai masukan kamu:**\n"
                "> 💡 **Kirim Saran** — ide dan usulan.\n"
                "> 🗣️ **Kirim Kritik** — evaluasi dan hal yang perlu diperbaiki."
            ),
            color=0xffffff
        )

        e.set_image(url=BANNER_URL)

        e.set_footer(
            text="Pak Tukang | Layanan Kritik & Saran"
        )

        # Kirim panel dengan dua tombol
        posted = await channel.send(
            embed=e,
            view=SaranView()
        )

        # Simpan konfigurasi server
        data = [
            x for x in saran()
            if x.get("guildId") != str(i.guild_id)
        ]

        data.append({
            "guildId": str(i.guild_id),
            "channelId": str(channel.id)
        })

        write("saran.json", data)

        await i.response.send_message(
            "✅ **Kotak Saran berhasil disiapkan!**\n"
            f"**Channel:** {channel.mention}\n"
            f"**Panel:** {posted.jump_url}",
            ephemeral=True
        )

    # =====================================================
    # SETUP MUTUALAN MEDIA SOSIAL
    # =====================================================

    @app_commands.command(
        name="setup-mutual-medsos",
        description="Membuat panel Mutualan Media Sosial"
    )
    @app_commands.default_permissions(manage_channels=True)
    @app_commands.describe(channel="Channel untuk panel Mutualan Media Sosial")
    async def setup_mutual_medsos(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
    ):
        panel = discord.Embed(
            description=(
                "# 📲 Mutualan Media Sosial\n"
                "Yuk, saling terhubung dengan warga Kampung Halaman!\n\n"
                "Tekan **Upload** untuk mengisi tautan media sosial kamu. "
                "Setelah profil dibuat, kamu dapat menggunakan tombol **Edit**, **Hapus**, atau **Upload** pada profilmu."
            ),
            color=discord.Color.from_rgb(255, 255, 255),
        )
        panel.set_image(url=BANNER_URL)
        panel.set_footer(text="Pak Tukang | Mutualan Media Sosial")

        message = await channel.send(embed=panel, view=MutualPanelView(self))
        configs = [
            item for item in mutual_settings()
            if item.get("guild_id") != str(interaction.guild_id)
        ]
        configs.append({
            "guild_id": str(interaction.guild_id),
            "channel_id": str(channel.id),
            "panel_message_id": str(message.id),
        })
        save_mutual_settings(configs)

        await interaction.response.send_message(
            f"✅ Panel Mutualan berhasil dibuat di {channel.mention}.\n"
            f"[Lihat panel]({message.jump_url})",
            ephemeral=True,
        )

    async def save_mutual_profile(self, interaction, values):
        if not interaction.guild:
            return await interaction.response.send_message(
                "Fitur ini hanya dapat digunakan di server.", ephemeral=True
            )

        cfg = next(
            (item for item in mutual_settings()
             if item.get("guild_id") == str(interaction.guild_id)),
            None,
        )
        if not cfg:
            return await interaction.response.send_message(
                "Panel Mutualan belum disiapkan administrator.", ephemeral=True
            )

        channel = interaction.guild.get_channel(int(cfg["channel_id"]))
        if not isinstance(channel, discord.TextChannel):
            return await interaction.response.send_message(
                "Channel Mutualan tidak ditemukan. Minta admin menjalankan setup ulang.",
                ephemeral=True,
            )

        data = mutual_profiles()
        profile = next(
            (item for item in data
             if item.get("guild_id") == str(interaction.guild_id)
             and item.get("user_id") == str(interaction.user.id)),
            None,
        )
        is_new = profile is None
        if is_new:
            profile = {
                "id": uuid.uuid4().hex[:12],
                "guild_id": str(interaction.guild_id),
                "user_id": str(interaction.user.id),
                "message_id": None,
                "thread_id": None,
            }

        profile.update(values)
        profile.pop("threads", None)
        profile["display_name"] = interaction.user.display_name
        profile["avatar_url"] = interaction.user.display_avatar.url

        try:
            if is_new:
                message = await channel.send(
                    embed=mutual_embed(profile),
                    view=MutualProfileView(self, profile),
                )
                profile["message_id"] = str(message.id)
                thread = await message.create_thread(
                    name="💬 Kolom Komentar",
                    auto_archive_duration=1440,
                    reason="Kolom komentar Mutualan Media Sosial",
                )
                profile["thread_id"] = str(thread.id)
            else:
                profile_message = await channel.fetch_message(int(profile["message_id"]))
                await profile_message.edit(
                    embed=mutual_embed(profile),
                    view=MutualProfileView(self, profile),
                )
        except discord.Forbidden:
            return await interaction.response.send_message(
                "Bot tidak memiliki izin mengirim/mengedit pesan atau membuat thread. "
                "Periksa Send Messages, Embed Links, Create Public Threads, dan "
                "Send Messages in Threads.",
                ephemeral=True,
            )
        except discord.HTTPException as exc:
            return await interaction.response.send_message(
                f"Profil gagal diproses oleh Discord: `{exc}`",
                ephemeral=True,
            )

        if is_new:
            data.append(profile)
        save_mutual_profiles(data)
        await interaction.response.send_message(
            "✅ Profil Mutualan kamu berhasil "
            + ("diunggah." if is_new else "diperbarui.")
            + "\n💬 Kolom komentar: 💬 Kolom Komentar",
            ephemeral=True,
        )


    # =====================================================
    # LISTENER AUTOTHREAD
    # =====================================================

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if (
            not message.guild
            or message.author.bot
            or not isinstance(
                message.channel,
                discord.TextChannel
            )
        ):
            return

        cfg = next(
            (
                x for x in configs()
                if x.get("channelId")
                == str(message.channel.id)
            ),
            None
        )

        if not cfg:
            return

        try:
            await message.create_thread(
                name=cfg.get("threadName", DEFAULT),
                auto_archive_duration=1440,
                reason="Auto Thread Pak Tukang"
            )
        except discord.HTTPException as ex:
            print(
                "Gagal membuat Auto Thread:",
                ex
            )
            return

        for emoji in cfg.get("reactions", []):
            try:
                await message.add_reaction(emoji)
            except discord.HTTPException as ex:
                print(
                    f"Gagal menambahkan reaksi "
                    f"{emoji}: {ex}"
                )

# =========================================================
# SETUP EXTENSION
# =========================================================

async def setup(bot: commands.Bot):
    # Registrasi persistent views.
    bot.add_view(SaranView())
    automasi_cog = Automasi(bot)
    bot.add_view(MutualPanelView(automasi_cog))
    for profile in mutual_profiles():
        if profile.get("message_id"):
            bot.add_view(
                MutualProfileView(automasi_cog, profile),
                message_id=int(profile["message_id"]),
            )
    await bot.add_cog(automasi_cog)
    await bot.add_cog(Feed(bot))


# =========================================================
# FEED WARGA (DIGABUNG DARI feed(8).py)
# =========================================================

CATEGORIES = [
    ("Berita & Informasi", "📰"),
    ("Dokumentasi", "📸"),
    ("Kehidupan Warga", "🏡"),
    ("Kegiatan", "🎉"),
    ("Umum", "🌐"),
]


def posts():
    return read("feed_posts.json", [])


def save_posts(data):
    write("feed_posts.json", data)


def settings():
    return read("feed_settings.json", [])


def save_settings(data):
    write("feed_settings.json", data)


def valid_url(value):
    if not value:
        return True

    parsed = urlparse(value)
    return (
        parsed.scheme in ("http", "https")
        and bool(parsed.netloc)
    )


def split_media_urls(value):
    """Split multiple URLs using the exact separator: space-pipe-space."""
    if not value:
        return []

    return [item.strip() for item in value.split(" | ") if item.strip()]


def get_link_platform(value):
    """Return a friendly platform name for normal web/social links."""
    if not value:
        return "Link"

    hostname = (urlparse(value).hostname or "").lower()
    if hostname.startswith("www."):
        hostname = hostname[4:]

    if hostname == "tiktok.com" or hostname.endswith(".tiktok.com"):
        return "TikTok"
    if hostname in ("x.com", "twitter.com") or hostname.endswith(".x.com") or hostname.endswith(".twitter.com"):
        return "X"
    if hostname == "instagram.com" or hostname.endswith(".instagram.com"):
        return "Instagram"

    return "Link"


def is_image_url(value):
    parsed = urlparse(value) if value else None
    return bool(
        parsed and parsed.path.lower().endswith(
            (".png", ".jpg", ".jpeg", ".gif", ".webp")
        )
    )


def post_embed(data):
    embed = discord.Embed(
        title=data.get("title") or "Postingan Warga",
        description=data.get("caption") or " ",
        color=discord.Color.from_rgb(255, 255, 255),
        timestamp=datetime.fromisoformat(data["created_at"]),
    )
    embed.set_author(
        name=data.get("author_name", "Warga Kampung Halaman"),
        icon_url=data.get("author_avatar") or discord.Embed.Empty,
    )
    # Compact metadata: only show the sender mention in the public post.
    embed.add_field(
        name="👤 Pengirim: ",
        value=f'<@{data["author_id"]}>',
        inline=True,
    )
    embed.add_field(
        name="🤔 Reaksi: ",
        value=(
            f'<:kh_like_brawlstars:1547921057393025066>: **{len(data.get("likes", []))}** | '
            f'<:kh_dislike_brawlstars:1547921092465655859>: **{len(data.get("dislikes", []))}**'
        ),
        inline=True,
    )

    # New format supports multiple URLs separated by " | ".
    # Old posts using media_url/media_type remain supported.
    media_urls = data.get("media_urls")
    if not media_urls:
        legacy_url = data.get("media_url")
        media_urls = [legacy_url] if legacy_url else []

    # Discord embeds can display one large image. If there is an image URL,
    # use the first image as the preview and keep every other URL clickable.
    image_url = next((url for url in media_urls if is_image_url(url)), None)
    if image_url:
        embed.set_image(url=image_url)

    # Keep all non-image links in ONE field. Each link gets a platform-specific
    # label (Instagram, TikTok, X, or Link) based on its hostname.
    link_lines = []
    for url in media_urls:
        if url == image_url:
            continue

        platform = get_link_platform(url)
        link_lines.append(f"• [{platform}]({url})")

    if link_lines:
        embed.add_field(
            name="🔗 Link",
            value="\n".join(link_lines),
            inline=False,
        )

    embed.set_footer(text="Kampung Halaman • Feed Warga")
    return embed


class CategorySelect(discord.ui.Select):
    def __init__(self, cog):
        self.cog = cog
        super().__init__(
            placeholder="Pilih kategori postingan...",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(label=name, emoji=emoji, value=name)
                for name, emoji in CATEGORIES
            ],
            custom_id="feed:category",
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(PostModal(self.cog, self.values[0]))


class CreateView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=300)
        self.add_item(CategorySelect(cog))


class PostModal(discord.ui.Modal):
    title_input = discord.ui.TextInput(
        label="Judul",
        placeholder="Judul postingan",
        max_length=200,
        required=True,
    )
    caption_input = discord.ui.TextInput(
        label="Caption / Informasi",
        style=discord.TextStyle.paragraph,
        placeholder="Ceritakan informasi yang ingin dibagikan...",
        max_length=3500,
        required=True,
    )
    media_input = discord.ui.TextInput(
        label="URL Media / Link (Opsional)",
        placeholder="Link Foto | Video | TikTok | X | Instagram | atau link lainnya...",
        max_length=500,
        required=False,
    )
    image_input = discord.ui.Label(
        text="Upload Image (opsional)",
        component=discord.ui.FileUpload(
            custom_id="feed_image",
            required=False,
        ),
    )

    def __init__(self, cog, category):
        super().__init__(title="Buat Postingan Feed")
        self.cog = cog
        self.category = category

    async def on_submit(self, interaction: discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message(
                "Gunakan fitur ini di server.", ephemeral=True
            )

        await interaction.response.defer(ephemeral=True, thinking=True)

        cfg = next(
            (item for item in settings()
             if item.get("guild_id") == str(interaction.guild_id)),
            None,
        )
        if not cfg:
            return await interaction.followup.send(
                "Feed belum disiapkan administrator.", ephemeral=True
            )

        channel = interaction.guild.get_channel(int(cfg["channel_id"]))
        if not isinstance(channel, discord.TextChannel):
            return await interaction.followup.send(
                "Channel Feed tidak ditemukan. Minta administrator menjalankan setup ulang.",
                ephemeral=True,
            )

        raw_media = (self.media_input.value or "").strip()
        media_urls = split_media_urls(raw_media)

        invalid_urls = [url for url in media_urls if not valid_url(url)]
        if invalid_urls:
            return await interaction.followup.send(
                "Semua URL harus berupa tautan HTTP/HTTPS yang valid. "
                'Pisahkan beberapa link dengan " | ".',
                ephemeral=True,
            )

        if len(media_urls) > 10:
            return await interaction.followup.send(
                "Maksimal 10 link dapat ditambahkan dalam satu postingan.",
                ephemeral=True,
            )

        # Discord FileUpload returns the selected attachment(s) in .values.
        # FileUpload is nested inside a Label in current discord.py modal APIs.
        file_component = getattr(self.image_input, "component", self.image_input)
        uploaded = getattr(file_component, "values", None) or []
        attachment = uploaded[0] if uploaded else None
        if attachment and not (getattr(attachment, "content_type", "") or "").startswith("image/"):
            return await interaction.followup.send(
                "File yang diunggah harus berupa gambar.", ephemeral=True
            )

        if attachment:
            # Keep an uploaded image together with any URLs entered in the form.
            media_urls.insert(0, attachment.url)

        media_type = "image" if media_urls and is_image_url(media_urls[0]) else (
            "link" if media_urls else None
        )
        final_media_url = media_urls[0] if media_urls else None
        link_platform = (
            get_link_platform(final_media_url)
            if final_media_url and media_type == "link"
            else None
        )

        emoji = dict(CATEGORIES)[self.category]
        data = {
            "id": uuid.uuid4().hex[:10],
            "guild_id": str(interaction.guild_id),
            "channel_id": str(channel.id),
            "message_id": None,
            "thread_id": None,
            "thread_url": None,
            "author_id": str(interaction.user.id),
            "author_name": interaction.user.display_name,
            "author_avatar": interaction.user.display_avatar.url,
            "title": self.title_input.value.strip(),
            "caption": self.caption_input.value.strip(),
            "category": self.category,
            "emoji": emoji,
            # Keep the new multi-link format while retaining legacy fields.
            "media_urls": media_urls,
            "media_url": final_media_url,
            "media_type": media_type,
            "link_platform": link_platform,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "likes": [],
            "dislikes": [],
        }

        try:
            message = await channel.send(
                embed=post_embed(data),
                view=PostView(self.cog, data["id"]),
            )
            data["message_id"] = str(message.id)

            # Create a public thread from the post and expose its direct link in the embed.
            thread = await message.create_thread(
                name="💬 Kolom Komentar",
                auto_archive_duration=1440,
            )
            data["thread_id"] = str(thread.id)
            data["thread_url"] = thread.jump_url
        except discord.Forbidden:
            return await interaction.followup.send(
                "Bot tidak memiliki izin mengirim postingan atau membuat thread. "
                "Periksa izin **Send Messages**, **Create Public Threads**, dan "
                "**Send Messages in Threads** pada channel Feed.",
                ephemeral=True,
            )
        except discord.HTTPException as exc:
            return await interaction.followup.send(
                f"Postingan gagal diproses oleh Discord: `{exc}`",
                ephemeral=True,
            )

        all_posts = posts()
        all_posts.append(data)
        save_posts(all_posts)

        # Send a moderation/audit copy to the configured log channel, if available.
        log_channel_id = cfg.get("log_channel_id")
        log_channel = (
            interaction.guild.get_channel(int(log_channel_id))
            if log_channel_id else None
        )
        if isinstance(log_channel, discord.TextChannel):
            log_embed = discord.Embed(
                title="🧾 Log Feed Warga",
                description=f"Postingan baru diterbitkan: [Lihat postingan]({message.jump_url})",
                color=discord.Color.blurple(),
                timestamp=datetime.now(timezone.utc),
            )
            log_embed.add_field(
                name="Pengirim",
                value=f"{interaction.user.mention}\n`{interaction.user.id}`",
                inline=False,
            )
            log_embed.add_field(name="ID Postingan", value=f'`{data["id"]}`', inline=True)
            log_embed.add_field(name="Judul", value=data["title"], inline=True)
            log_embed.add_field(
                name="Kategori",
                value=f"{emoji} {self.category}",
                inline=True,
            )
            try:
                await log_channel.send(embed=log_embed)
            except discord.HTTPException:
                pass

        # Upload berhasil. Jangan tinggalkan ephemeral message setelah proses selesai.
        # Gunakan original interaction response lalu hapus kembali.
        await interaction.edit_original_response(
            content=(
                f"✅ Postingan diterbitkan: {message.jump_url}\n"
                f"💬 Kolom komentar: {data['thread_url']}"
            )
        )
        await interaction.delete_original_response()


class EditPostModal(discord.ui.Modal):
    def __init__(self, cog, post_id, data):
        super().__init__(title="Edit Postingan Feed")
        self.cog = cog
        self.post_id = post_id
        self.original_data = data

        current_urls = data.get("media_urls")
        if not current_urls:
            legacy_url = data.get("media_url")
            current_urls = [legacy_url] if legacy_url else []

        self.title_input = discord.ui.TextInput(
            label="Judul",
            placeholder="Judul postingan",
            default=data.get("title", ""),
            max_length=200,
            required=True,
        )
        self.caption_input = discord.ui.TextInput(
            label="Caption / Informasi",
            style=discord.TextStyle.paragraph,
            placeholder="Ceritakan informasi yang ingin dibagikan...",
            default=data.get("caption", ""),
            max_length=3500,
            required=True,
        )
        self.media_input = discord.ui.TextInput(
            label="URL Media / Link (Opsional)",
            placeholder="Gunakan \" | \" untuk beberapa link",
            default=" | ".join(current_urls),
            max_length=500,
            required=False,
        )

        self.add_item(self.title_input)
        self.add_item(self.caption_input)
        self.add_item(self.media_input)

    async def on_submit(self, interaction: discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message(
                "Gunakan fitur ini di server.", ephemeral=True
            )

        all_posts = posts()
        data = next((item for item in all_posts if item["id"] == self.post_id), None)
        if not data:
            return await interaction.response.send_message(
                "Postingan tidak ditemukan.", ephemeral=True
            )

        # Only the original author may edit the post.
        is_author = str(interaction.user.id) == str(data.get("author_id"))
        if not is_author:
            return await interaction.response.send_message(
                "Kamu hanya dapat mengedit postingan milikmu sendiri.",
                ephemeral=True,
            )

        raw_media = (self.media_input.value or "").strip()
        media_urls = split_media_urls(raw_media)

        invalid_urls = [url for url in media_urls if not valid_url(url)]
        if invalid_urls:
            return await interaction.response.send_message(
                "Semua URL harus berupa tautan HTTP/HTTPS yang valid. "
                'Pisahkan beberapa link dengan " | ".',
                ephemeral=True,
            )

        if len(media_urls) > 10:
            return await interaction.response.send_message(
                "Maksimal 10 link dapat ditambahkan dalam satu postingan.",
                ephemeral=True,
            )

        # Update the post data without touching likes, dislikes, author,
        # category, creation time, message ID, or comment thread.
        data["title"] = self.title_input.value.strip()
        data["caption"] = self.caption_input.value.strip()
        data["media_urls"] = media_urls
        data["media_url"] = media_urls[0] if media_urls else None
        data["media_type"] = (
            "image" if media_urls and is_image_url(media_urls[0])
            else ("link" if media_urls else None)
        )
        data["link_platform"] = (
            get_link_platform(media_urls[0])
            if media_urls and data["media_type"] == "link"
            else None
        )

        message = interaction.message
        if not message:
            channel = interaction.guild.get_channel(int(data["channel_id"]))
            if isinstance(channel, discord.TextChannel):
                try:
                    message = await channel.fetch_message(int(data["message_id"]))
                except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                    message = None

        if not message:
            return await interaction.response.send_message(
                "Pesan postingan tidak dapat ditemukan di channel Feed.",
                ephemeral=True,
            )

        try:
            await message.edit(
                embed=post_embed(data),
                view=PostView(self.cog, self.post_id),
            )
        except discord.Forbidden:
            return await interaction.response.send_message(
                "Bot tidak memiliki izin untuk mengedit postingan tersebut.",
                ephemeral=True,
            )
        except discord.HTTPException as exc:
            return await interaction.response.send_message(
                f"Postingan gagal diperbarui oleh Discord: `{exc}`",
                ephemeral=True,
            )

        save_posts(all_posts)

        await interaction.response.send_message(
            "✅ Postingan berhasil diperbarui.",
            ephemeral=True,
        )


class PostView(discord.ui.View):
    def __init__(self, cog, post_id):
        super().__init__(timeout=None)
        self.cog = cog
        self.post_id = post_id
        self.add_item(discord.ui.Button(
            emoji="<:kh_like_brawlstars:1547921057393025066>",
            style=discord.ButtonStyle.primary,
            custom_id=f"feed:like:{post_id}",
        ))
        self.add_item(discord.ui.Button(
            emoji="<:kh_dislike_brawlstars:1547921092465655859>",
            style=discord.ButtonStyle.danger,
            custom_id=f"feed:dislike:{post_id}",
        ))
        self.add_item(discord.ui.Button(
            label="Edit",
            emoji="✏️",
            style=discord.ButtonStyle.secondary,
            custom_id=f"feed:edit:{post_id}",
        ))
        self.add_item(discord.ui.Button(
            label="Upload",
            emoji="📝",
            style=discord.ButtonStyle.success,
            custom_id=f"feed:upload:{post_id}",
        ))
        for item in self.children:
            item.callback = self.handle

    async def handle(self, interaction: discord.Interaction):
        action, post_id = interaction.data["custom_id"].split(":")[1:]
        all_posts = posts()
        data = next((item for item in all_posts if item["id"] == post_id), None)
        if not data:
            return await interaction.response.send_message(
                "Postingan tidak ditemukan.", ephemeral=True
            )

        if action == "edit":
            # Only the original author may open the edit form.
            is_author = str(interaction.user.id) == str(data.get("author_id"))
            if not is_author:
                return await interaction.response.send_message(
                    "Kamu hanya dapat mengedit postingan milikmu sendiri.",
                    ephemeral=True,
                )

            return await interaction.response.send_modal(
                EditPostModal(self.cog, post_id, data)
            )

        if action == "upload":
            return await interaction.response.send_message(
                "Pilih kategori postingan:",
                view=CreateView(self.cog),
                ephemeral=True,
            )

        if action not in ("like", "dislike"):
            return await interaction.response.send_message(
                "Aksi tidak dikenali.", ephemeral=True
            )

        user_id = str(interaction.user.id)
        likes = data.setdefault("likes", [])
        dislikes = data.setdefault("dislikes", [])
        own, other = (likes, dislikes) if action == "like" else (dislikes, likes)

        if user_id in own:
            own.remove(user_id)
        else:
            if user_id in other:
                other.remove(user_id)
            own.append(user_id)

        save_posts(all_posts)
        try:
            await interaction.message.edit(
                embed=post_embed(data),
                view=PostView(self.cog, post_id),
            )
        except discord.HTTPException:
            pass

        await interaction.response.send_message(
            f"<:kh_like_brawlstars:1547921057393025066> {len(likes)}  |  <:kh_dislike_brawlstars:1547921092465655859> {len(dislikes)}",
            ephemeral=True,
        )


class Feed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        self.bot.add_view(FeedPanelView(self))
        for post in posts():
            self.bot.add_view(PostView(self, post["id"]))

    @app_commands.command(
        name="setup-feed",
        description="Menyiapkan panel Feed Warga",
    )
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.describe(
        channel="Channel utama untuk seluruh postingan Feed",
        log_channel="Channel untuk mencatat log postingan Feed",
    )
    async def setup_feed(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        log_channel: discord.TextChannel,
    ):
        if not interaction.guild:
            return await interaction.response.send_message(
                "Gunakan di server.", ephemeral=True
            )

        await interaction.response.defer(ephemeral=True, thinking=True)

        embed = discord.Embed(
            description=(
                "# 📱 Feed Warga\nBagikan berita, informasi, dokumentasi, kegiatan, dan cerita warga di sini.\n\n"
                "**Cara membuat postingan:** tekan tombol **Upload**, pilih "
                'kategori, lalu isi judul, caption, URL media/link, dan/atau unggah gambar '
                'jika diperlukan. Untuk beberapa link, gunakan pemisah "` | `". '
                "URL dan gambar bersifat Opsional."
            ),
            color=discord.Color.from_rgb(255, 255, 255),
        )
        embed.set_image(url=BANNER_URL)
        embed.set_footer(text="Pak Tukang • Feed Warga")

        try:
            panel_message = await channel.send(
                embed=embed,
                view=FeedPanelView(self),
            )
        except discord.Forbidden:
            return await interaction.followup.send(
                "Bot tidak memiliki izin mengirim pesan di channel Feed.",
                ephemeral=True,
            )

        saved = [
            item for item in settings()
            if item.get("guild_id") != str(interaction.guild_id)
        ]
        saved.append({
            "guild_id": str(interaction.guild_id),
            "channel_id": str(channel.id),
            "log_channel_id": str(log_channel.id),
            "panel_message_id": str(panel_message.id),
        })
        save_settings(saved)

        await interaction.followup.send(
            f"✅ Feed disiapkan di {channel.mention}\n"
            f"🧾 Log: {log_channel.mention}\n"
            f"{panel_message.jump_url}",
            ephemeral=True,
        )

    @app_commands.command(
        name="buat-postingan",
        description="Membuat postingan Feed Warga",
    )
    async def buat_postingan(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Pilih kategori postingan:",
            view=CreateView(self),
            ephemeral=True,
        )


class FeedPanelView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(
        label="Upload",
        emoji="📝",
        style=discord.ButtonStyle.primary,
        custom_id="feed:open",
    )
    async def open(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "Pilih kategori postingan:",
            view=CreateView(self.cog),
            ephemeral=True,
        )