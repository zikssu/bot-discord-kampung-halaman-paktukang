async def load_extensions(bot):
    extensions = [
        "bot.commands.bantuan",
        "bot.commands.utilitas",
        "bot.commands.automasi",
    ]

    for name in extensions:
        print(f"Memuat extension: {name}")
        await bot.load_extension(name)