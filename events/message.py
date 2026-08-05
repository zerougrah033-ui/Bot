import discord
import time
from collections import defaultdict

from ai.moderation import check_message
from utils.punish import punish
from utils.protection import is_protected


# ==========================
# SETTINGS
# ==========================

LOG_CHANNEL_ID = 1525906374628741192


SPAM_LIMIT = 5
SPAM_WINDOW = 5


# تخزين رسائل الأعضاء
spam = defaultdict(list)


# ==========================
# MESSAGE EVENT
# ==========================

async def setup(bot):

    @bot.event
    async def on_message(message: discord.Message):
        print("MESSAGE EVENT:", message.content)

        # تجاهل البوتات
        if message.author.bot:
            return

        # تجاهل الخاص
        if not message.guild:
            return


        # ==========================
        # ANTI SPAM
        # ==========================

        uid = message.author.id
        now = time.time()

        spam[uid].append(now)

        spam[uid] = [
            t for t in spam[uid]
            if now - t < SPAM_WINDOW
        ]


        if len(spam[uid]) >= SPAM_LIMIT:

            await message.delete()

            if not is_protected(message.author):

                warns, action = await punish(
                    message.author,
                    "Spam"
                )

                await send_log(
                    bot,
                    message,
                    "Spam",
                    warns,
                    action
                )

            else:

                await send_log(
                    bot,
                    message,
                    "Spam (Staff)",
                    0,
                    "No Punishment"
                )


            spam[uid].clear()
            return


        # ==========================
        # GEMINI MODERATION
        # ==========================

        result = await check_message(
            message.content
        )
                if result["toxic"]:

            try:
                await message.delete()
            except discord.Forbidden:
                pass

            # رسالة مؤقتة للعضو
            try:
                warn_msg = await message.channel.send(
                    f"{message.author.mention} ⚠️ يمنع استخدام الألفاظ المسيئة."
                )
                await warn_msg.delete(delay=5)
            except Exception:
                pass

            # إرسال لوق للإدارة
            await send_log(
                bot,
                message,
                result["reason"],
                0,
                "Deleted Message",
                result["score"]
            )

            return

        await bot.process_commands(message)



# ==========================
# LOG EMBED
# ==========================

async def send_log(
    bot,
    message,
    reason,
    warns,
    action,
    score=0
):

    channel = bot.get_channel(
        LOG_CHANNEL_ID
    )

    if not channel:
        return


    embed = discord.Embed(
        title="🚨 Moderation Alert",
        color=discord.Color.red()
    )


    embed.add_field(
        name="👤 العضو",
        value=message.author.mention,
        inline=False
    )


    embed.add_field(
        name="💬 الرسالة",
        value=message.content[:1024],
        inline=False
    )


    embed.add_field(
        name="📌 السبب",
        value=reason,
        inline=True
    )


    embed.add_field(
        name="📊 AI Score",
        value=f"{score}%",
        inline=True
    )


    embed.add_field(
        name="⚠️ التحذيرات",
        value=str(warns),
        inline=True
    )


    embed.add_field(
        name="🔨 العقوبة",
        value=action,
        inline=True
    )


    embed.set_footer(
        text="AI Moderation System"
    )


    await channel.send(
        embed=embed
  )
