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


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        for folder in ["events", "commands"]:
            if os.path.exists(folder):
                for file in os.listdir(folder):
                    if file.endswith(".py"):
                        await self.load_extension(f"{folder}.{file[:-3]}")
                        print(f"Loaded -> {folder}.{file[:-3]}")

        await self.tree.sync()
        print("Slash Commands Synced ✅")


bot = MyBot()

bot.run(TOKEN)
