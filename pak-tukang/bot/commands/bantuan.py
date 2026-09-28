import discord
from discord import app_commands
from discord.ext import commands

BANNER_URL = "https://cdn.discordapp.com/attachments/1545650023793041439/1553221942981558312/banner-server-discord-Kampung-Halaman-Garis.png?ex=6abb1928&is=6ab9c7a8&hm=3c2352b28839311353fab815a8f03d7f4cbbd078e86868ff24c72d17b7873531"

class HelpSelect(discord.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="Pilih kategori...",
            custom_id="bantuan:kategori",
            options=[
                discord.SelectOption(
                    label="Beranda",
                    description="Informasi Utama mengenai Bot Tukang.",
                    value="utama",
                    emoji="🏠"
                ),
                discord.SelectOption(
                    label="Utilitas",
                    description="Informasi Tools Command Discord.",
                    value="utilitas",
                    emoji="🛠️"
                ),
                discord.SelectOption(
                    label="Automasi",
                    description="Informasi Tools Automasi.",
                    value="automasi",
                    emoji="⚙️"
                )
            ]
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            embed=make_embed(self.values[0]),
            view=self.view
        )


class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(HelpSelect())


def make_embed(category):
    e = discord.Embed(color=0xffffff)

    if category == "utilitas":
        e.description = (
            "# 🛠️ Utilitas\n"
            "Informasi server, profil pengguna, dan tools pemeriksaan bot.\n\n"
            "- `/infoserver` — Informasi mengenai server Discord.\n"
            "- `/infouser` — Informasi Profil pengguna Discord.\n"
            "- `/ping` — Informasi Latensi Bot Pak Tukang."
        )

    elif category == "automasi":
        e.description = (
            "# ⚙️ Automasi\n"
            "Fitur untuk mengelola aktivitas Kampung Halaman.\n\n"
            "- `/autothread` — Mengatur Auto Thread.\n"
            "- `/daftar-autothread` — Informasi Daftar channel "
            "yang menggunakan Auto Thread.\n"
            "- `/setup-saran` — Membuat panel Kritik & Saran."
        )

    else:
        e.description = (
            "# 👷‍♂️ Halo! Saya Pak Tukang.\n"
            "-# Prefix `/` | Mention <@1553311149850628156>\n\n"
            "Saya adalah **bot serbaguna (All in One Bot)** "
            "untuk membantu mengelola, merawat, dan mengembangkan "
            "komunitas **Kampung Halaman**. 🏡\n\n"
            "> Pilih kategori dari menu di bawah untuk melihat command."
        )

    # Banner Kampung Halaman di bagian bawah embed
    e.set_image(url=BANNER_URL)

    return e


class Bantuan(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="bantuan",
        description="Menampilkan pusat bantuan Pak Tukang"
    )
    async def bantuan(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            embed=make_embed("utama"),
            view=HelpView(),
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Bantuan(bot))