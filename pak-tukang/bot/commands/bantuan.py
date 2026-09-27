import discord
from discord import app_commands
from discord.ext import commands
class HelpSelect(discord.ui.Select):
    def __init__(self):
        super().__init__(placeholder="Pilih kategori...",custom_id="bantuan:kategori",options=[
            discord.SelectOption(label="Beranda",description="Informasi utama Pak Tukang",value="utama",emoji="🏠"),
            discord.SelectOption(label="Utilitas",description="Informasi dan tools Discord",value="utilitas",emoji="🛠️"),
            discord.SelectOption(label="Automasi",description="Fitur otomatisasi server",value="automasi",emoji="⚙️")])
    async def callback(self, interaction):
        await interaction.response.edit_message(embed=make_embed(self.values[0]),view=self.view)
class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None); self.add_item(HelpSelect())
def make_embed(category):
    e=discord.Embed(color=0xffffff)
    if category=="utilitas":
        e.title="🛠️ Utilitas"; e.description="Informasi server, profil pengguna, dan tools pemeriksaan bot.\n\n/infoserver — Informasi server Discord\n/infouser — Profil pengguna Discord\n/ping — Latensi Pak Tukang"
    elif category=="automasi":
        e.title="⚙️ Automasi"; e.description="Fitur untuk mengelola aktivitas Kampung Halaman.\n\n/autothread — Mengatur Auto Thread\n/daftar-autothread — Daftar channel Auto Thread\n/setup-saran — Membuat panel Kritik & Saran"
    else:
        e.description="# 👷‍♂️ Halo! Saya Pak Tukang.\n-# Prefix `/` | Mention <@1553311149850628156>\n\nSaya adalah **bot serbaguna (All in One Bot)** untuk membantu mengelola, merawat, dan mengembangkan komunitas **Kampung Halaman**. 🏡\n\n> Pilih kategori dari menu di bawah untuk melihat command."
    return e
class Bantuan(commands.Cog):
    def __init__(self,bot): self.bot=bot
    @app_commands.command(name="bantuan",description="Menampilkan pusat bantuan Pak Tukang")
    async def bantuan(self,interaction:discord.Interaction):
        await interaction.response.send_message(embed=make_embed("utama"),view=HelpView(),ephemeral=True)
async def setup(bot): await bot.add_cog(Bantuan(bot))
