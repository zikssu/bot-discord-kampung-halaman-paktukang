import discord
from discord import app_commands
from discord.ext import commands
from bot.store import read,write
DEFAULT="💬 Kolom Komentar"
def configs(): return read("autothread.json",[])
def saran(): return read("saran.json",[])
class SaranModal(discord.ui.Modal,title="💡 Kritik & Saran"):
    isi=discord.ui.TextInput(label="Masukkan Kritik/Saran di bawah ini.",style=discord.TextStyle.paragraph,placeholder="Tuliskan ide, kritik, atau saran kamu...",max_length=4000)
    async def on_submit(self,i):
        value=self.isi.value.strip()
        if not value: return await i.response.send_message("❌ Kritik atau saran tidak boleh kosong.",ephemeral=True)
        cfg=next((x for x in saran() if x["guildId"]==str(i.guild_id)),None)
        if not cfg: return await i.response.send_message("❌ Kotak Saran belum diatur oleh staf.",ephemeral=True)
        ch=i.guild.get_channel(int(cfg["channelId"]))
        if not isinstance(ch,discord.TextChannel): return await i.response.send_message("❌ Channel Kotak Saran tidak ditemukan.",ephemeral=True)
        e=discord.Embed(description=f"# 💡 Kritik & Saran Baru\n**Pengirim:** {i.user.mention}\n\n**Kritik & Saran:**\n{value}",color=0xffffff,timestamp=discord.utils.utcnow())
        e.set_author(name=i.user.name,icon_url=i.user.display_avatar.url); e.set_footer(text="Kampung Halaman | Kotak Saran")
        post=await ch.send(embed=e); thread=await post.create_thread(name=DEFAULT,auto_archive_duration=1440)
        await post.add_reaction("⬆️"); await post.add_reaction("⬇️")
        await i.response.send_message(f"✅ **Kritik & saran berhasil dikirim!**\n📨 Postingan: {post.jump_url}\n💬 Kolom Komentar: {thread.mention}",ephemeral=True)
class SaranView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="Kirim Saran",emoji="📝",style=discord.ButtonStyle.primary,custom_id="saran:open")
    async def open(self,i,b): await i.response.send_modal(SaranModal())
class Automasi(commands.Cog):
    def __init__(self,bot): self.bot=bot
    @app_commands.command(name="autothread",description="Tambah atau hapus Auto Thread")
    @app_commands.default_permissions(manage_channels=True)
    @app_commands.describe(aksi="Pilih tindakan",channel="Channel teks",reaksi="Emoji dipisahkan spasi")
    @app_commands.choices(aksi=[app_commands.Choice(name="Menambahkan (Add)",value="tambah"),app_commands.Choice(name="Menghapus (Remove)",value="hapus")])
    async def autothread(self,i:discord.Interaction,aksi:app_commands.Choice[str],channel:discord.TextChannel,reaksi:str=""):
        data=configs(); old=next((x for x in data if x.get("channelId")==str(channel.id)),None)
        if aksi.value=="tambah":
            if old: return await i.response.send_message("Channel tersebut sudah menggunakan Auto Thread.",ephemeral=True)
            reactions=reaksi.split()
            data.append({"channelId":str(channel.id),"threadName":DEFAULT,"reactions":reactions}); write("autothread.json",data)
            return await i.response.send_message(f"Auto Thread berhasil ditambahkan!\n**Channel:** {channel.mention}\n**Nama Thread:** {DEFAULT}\n**Auto Reaction:** {' '.join(reactions) or 'Tidak ada'}",ephemeral=True)
        if not old: return await i.response.send_message("Channel tersebut belum terdaftar di Auto Thread.",ephemeral=True)
        write("autothread.json",[x for x in data if x.get("channelId")!=str(channel.id)])
        await i.response.send_message(f"Auto Thread berhasil dihapus dari {channel.mention}.",ephemeral=True)
    @app_commands.command(name="daftar-autothread",description="Menampilkan daftar channel Auto Thread")
    @app_commands.default_permissions(manage_channels=True)
    async def daftar(self,i):
        rows=[]
        for n,x in enumerate(configs(),1):
            ch=i.guild.get_channel(int(x["channelId"])) if i.guild else None
            if ch: rows.append(f"**{n}.** {ch.mention}\n> Nama Thread: {DEFAULT}\n> Auto Reaction: {' '.join(x.get('reactions',[])) or 'Tidak ada'}")
        await i.response.send_message("**📋 Daftar Auto Thread**\n\n"+"\n\n".join(rows) if rows else "Belum ada channel yang menggunakan Auto Thread.",ephemeral=True)
    @app_commands.command(name="setup-saran",description="Mengatur channel khusus Kritik & Saran")
    @app_commands.default_permissions(manage_channels=True)
    @app_commands.describe(channel="Channel untuk Kotak Saran")
    async def setup_saran(self,i,channel:discord.TextChannel):
        e=discord.Embed(description="# 💡 Kotak Kritik & Saran\nPunya ide, kritik, atau saran untuk Kampung Halaman? Sampaikan melalui formulir di bawah ini. Setiap masukan membantu warga membangun komunitas bersama.\n\n**📝 Tekan tombol Kirim Saran untuk memulai.**",color=0xffffff)
        e.set_footer(text="Pak Tukang | Layanan Kritik & Saran")
        posted=await channel.send(embed=e,view=SaranView())
        data=[x for x in saran() if x.get("guildId")!=str(i.guild_id)]; data.append({"guildId":str(i.guild_id),"channelId":str(channel.id)}); write("saran.json",data)
        await i.response.send_message(f"✅ Kotak Saran berhasil disiapkan di {channel.mention}.\nPanel: {posted.jump_url}",ephemeral=True)
    @commands.Cog.listener()
    async def on_message(self,message):
        if not message.guild or message.author.bot or not isinstance(message.channel,discord.TextChannel): return
        cfg=next((x for x in configs() if x.get("channelId")==str(message.channel.id)),None)
        if not cfg: return
        try: await message.create_thread(name=DEFAULT,auto_archive_duration=1440,reason="Auto Thread Pak Tukang")
        except discord.HTTPException as ex: print("Gagal membuat Auto Thread:",ex); return
        for emoji in cfg.get("reactions",[]):
            try: await message.add_reaction(emoji)
            except discord.HTTPException as ex: print(f"Gagal menambahkan reaksi {emoji}:",ex)
async def setup(bot):
    bot.add_view(SaranView())
    await bot.add_cog(Automasi(bot))
