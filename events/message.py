import time
import discord

from discord.ext import commands
from collections import defaultdict

from ai.moderation import check_message
from utils.logger import send_log
from utils.punish import punish
from utils.protection import is_protected


SPAM_LIMIT = 5
SPAM_WINDOW = 5

spam_cache = defaultdict(list)


class MessageEvents(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        # تجاهل البوتات والرسائل الخاصة
        if message.author.bot or message.guild is None:
            return

        print("MESSAGE:", message.content)

        # تشغيل الأوامر
        await self.bot.process_commands(message)

        # ==========================
        # AI MODERATION
        # ==========================

        ai_result = await check_message(message.content)

        if ai_result["toxic"]:

            score = int(ai_result["score"])
            reason = ai_result["reason"]

            try:
                await message.delete()
            except discord.Forbidden:
                pass
                # الإدارة والمالك
                if is_protected(message.author):

                     embed = discord.Embed(
        title="⚠️ Staff Message Removed",
        color=discord.Color.orange()
    )

    embed.set_thumbnail(
        url=message.author.display_avatar.url
    )

    embed.add_field(
        name="👤 Staff",
        value=message.author.mention,
        inline=False
    )

    embed.add_field(
        name="💬 Message",
        value=f"```{message.content[:1000]}```",
        inline=False
    )

    embed.add_field(
        name="🏷️ Reason",
        value=reason,
        inline=True
    )

    embed.add_field(
        name="📈 AI Score",
        value=f"{score}%",
        inline=True
    )

    embed.add_field(
        name="📝 Action",
        value="Message Deleted Only",
        inline=False
    )

    embed.add_field(
        name="📍 Channel",
        value=message.channel.mention,
        inline=False
    )

    embed.set_footer(
        text="Mafia Bot • AI Moderation"
    )

    await send_log(self.bot, embed)

    return
                        # ==========================
        # AI PUNISHMENT
        # ==========================

        warns, action = await punish(
            message.author,
            "AI Toxic Message"
        )

        embed = discord.Embed(
            title="🤖 AI Moderation",
            color=discord.Color.orange()
        )

        embed.set_thumbnail(
            url=message.author.display_avatar.url
        )

        embed.add_field(
            name="👤 Member",
            value=f"{message.author.mention}\n`{message.author.id}`",
            inline=False
        )

        embed.add_field(
            name="💬 Message",
            value=f"```{message.content[:1000]}```",
            inline=False
        )

        embed.add_field(
            name="🏷️ Reason",
            value=reason,
            inline=True
        )

        embed.add_field(
            name="📈 AI Score",
            value=f"{score}%",
            inline=True
        )

        embed.add_field(
            name="📊 Warnings",
            value=str(warns),
            inline=True
        )

        embed.add_field(
            name="⛔ Action",
            value=action,
            inline=True
        )

        embed.add_field(
            name="📍 Channel",
            value=message.channel.mention,
            inline=False
        )

        embed.set_footer(
            text="Mafia Bot • AI Moderation"
        )

        await send_log(self.bot, embed)

        return
                # ==========================
        # ANTI SPAM
        # ==========================

        uid = message.author.id
        now = time.time()

        spam_cache[uid].append(now)

        spam_cache[uid] = [
            t for t in spam_cache[uid]
            if now - t <= SPAM_WINDOW
        ]

        if len(spam_cache[uid]) >= SPAM_LIMIT:

            try:
                await message.channel.purge(
                    limit=SPAM_LIMIT,
                    check=lambda m: m.author.id == uid
                )

            except discord.Forbidden:
                pass

            warns, action = await punish(
                message.author,
                "Spam"
            )

            embed = discord.Embed(
                title="🚨 Anti Spam Detected",
                color=discord.Color.red()
            )

            embed.set_thumbnail(
                url=message.author.display_avatar.url
            )

            embed.add_field(
                name="👤 Member",
                value=f"{message.author.mention}\n`{message.author.id}`",
                inline=False
            )

            embed.add_field(
                name="📝 Reason",
                value="Spam",
                inline=True
            )

            embed.add_field(
                name="📊 Warnings",
                value=str(warns),
                inline=True
            )

            embed.add_field(
                name="⛔ Action",
                value=action,
                inline=False
            )

            embed.add_field(
                name="💬 Messages",
                value=f"{SPAM_LIMIT} messages in {SPAM_WINDOW} seconds",
                inline=False
            )

            embed.add_field(
                name="📍 Channel",
                value=message.channel.mention,
                inline=False
            )

            embed.set_footer(
                text="Mafia Bot • Anti Spam"
            )

            await send_log(
                self.bot,
                embed
            )

            spam_cache[uid].clear()


async def setup(bot):
    await bot.add_cog(MessageEvents(bot))
