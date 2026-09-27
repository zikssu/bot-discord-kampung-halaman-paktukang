import os
async def load_extensions(bot):
    for name in ["bot.commands.bantuan","bot.commands.utilitas","bot.commands.automasi"]:
        await bot.load_extension(name)
