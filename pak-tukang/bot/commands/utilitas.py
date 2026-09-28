import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime

BANNER_URL = "https://cdn.discordapp.com/attachments/1545650023793041439/1553221942981558312/banner-server-discord-Kampung-Halaman-Garis.png?ex=6abb1928&is=6ab9c7a8&hm=3c2352b28839311353fab815a8f03d7f4cbbd078e86868ff24c72d17b7873531"
class Utilitas(commands.Cog):
    def __init__(self,bot): self.bot=bot
    @app_commands.command(name="ping",description="Memeriksa latensi Pak Tukang")
    async def ping(self,i:discord.Interaction):
        await i.response.send_message(f"🏓 **Pong!**\nWebSocket: `{round(self.bot.latency*1000)} ms`",ephemeral=True)
    @app_commands.command(name="infoserver",description="Melihat informasi server Discord")
    async def infoserver(self,i:discord.Interaction):
        g=i.guild
        if not g: return await i.response.send_message("Command ini hanya bisa digunakan di server.",ephemeral=True)
        owner=g.owner or await g.fetch_member(g.owner_id)
        e=discord.Embed(title="🏡 Informasi Server",color=0xffffff,description=f"**Nama:** {g.name}\n**ID:** {g.id}\n**Pemilik:** {owner}\n**Jumlah anggota:** {g.member_count}\n**Dibuat:** <t:{int(g.created_at.timestamp())}:D>")
        e.set_image(url=BANNER_URL)
        await i.response.send_message(embed=e,ephemeral=True)
    @app_commands.command(name="infouser",description="Melihat informasi pengguna Discord")
    @app_commands.describe(pengguna="Pengguna yang ingin diperiksa")
    async def infouser(self,i:discord.Interaction,pengguna:discord.User=None):
        u=pengguna or i.user
        m=i.guild.get_member(u.id) if i.guild else None
        s=f"# 👤 Informasi Pengguna\n**Username:** {u}\n**ID:** {u.id}\n**Bot:** {'Ya' if u.bot else 'Tidak'}\n**Akun dibuat:** <t:{int(u.created_at.timestamp())}:D>"
        if m and m.joined_at: s+=f"\n**Bergabung ke server:** <t:{int(m.joined_at.timestamp())}:D>"
        await i.response.send_message(s,ephemeral=True)
async def setup(bot): await bot.add_cog(Utilitas(bot))

