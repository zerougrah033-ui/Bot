import discord
from discord.ext import commands

from config import TOKEN

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

@bot.event
async def on_ready():
    print("=" * 40)
    print(f"Logged in as: {bot.user}")
    print(f"Connected to {len(bot.guilds)} server(s)")
    print("Bot is ready ✅")
    print("=" * 40)

bot.run(TOKEN)
