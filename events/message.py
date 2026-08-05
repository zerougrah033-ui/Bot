import time
import discord
from discord.ext import commands
from collections import defaultdict

from utils.punish import punish

# الإعدادات
SPAM_LIMIT = 5      # عدد الرسائل
SPAM_WINDOW = 5     # خلال كم ثانية

spam_cache = defaultdict(list)


class MessageEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        # تجاهل البوتات
        if message.author.bot:
            return

        # تجاهل الخاص
        if message.guild is None:
            return

        # السماح للأوامر بالعمل
        await self.bot.process_commands(message)

        uid = message.author.id
        now = time.time()

        spam_cache[uid].append(now)

        # حذف الرسائل القديمة من القائمة
        spam_cache[uid] = [
            t for t in spam_cache[uid]
            if now - t <= SPAM_WINDOW
        ]

        # إذا وصل الحد
        if len(spam_cache[uid]) >= SPAM_LIMIT:

            try:
                await message.channel.purge(
                    limit=SPAM_LIMIT,
                    check=lambda m: m.author.id == uid
                )
            except discord.Forbidden:
                pass

            warns = await punish(
                message.author,
                "Spam"
            )

            await message.channel.send(
                f"⚠️ {message.author.mention} تم اكتشاف Spam.\n"
                f"عدد التحذيرات: **{warns}**",
                delete_after=8
            )

            spam_cache[uid].clear()


async def setup(bot):
    await bot.add_cog(MessageEvents(bot))
