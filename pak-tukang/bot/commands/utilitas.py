import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
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
