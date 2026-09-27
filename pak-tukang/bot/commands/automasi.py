
import discord
from discord import app_commands
from discord.ext import commands

from bot.store import read, write


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
                "❌ Kritik atau saran tidak boleh kosong.",
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

        # Embed masukan
        e = discord.Embed(
            description=(
                f"# {emoji} {self.jenis} Baru\n"
                f"👤 **Pengirim**: {i.user.mention}\n\n"
                f"✉️ **{self.jenis}**:\n{isi_berformat}"
            ),
            color=0xffffff,
            timestamp=discord.utils.utcnow()
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
    # Registrasi persistent view agar tombol tetap
    # berfungsi setelah bot restart.
    bot.add_view(SaranView())

    await bot.add_cog(
        Automasi(bot)
    )