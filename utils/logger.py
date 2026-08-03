import discord
from config import LOG_CHANNEL_ID


async def send_log(bot, embed: discord.Embed):
    channel = bot.get_channel(LOG_CHANNEL_ID)

    if channel is None:
        return

    await channel.send(embed=embed)
