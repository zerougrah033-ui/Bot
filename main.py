import os
import discord
from discord.ext import commands
from config import TOKEN

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.messages = True
intents.voice_states = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)


@bot.event
async def setup_hook():
    for folder in ["events", "commands"]:
        await bot.tree.sync()
        print("Slash Commands Synced ✅")
        if os.path.exists(folder):
            for file in os.listdir(folder):
                if file.endswith(".py"):
                    await bot.load_extension(f"{folder}.{file[:-3]}")
                    print(f"Loaded -> {folder}.{file[:-3]}")


bot.run(TOKEN)
