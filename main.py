import discord
from discord.ext import commands
import datetime
import asyncio
import time
import os
from collections import defaultdict

# ==========================
# CONFIG
# ==========================

TOKEN = os.getenv("TOKEN")

LOG_CHANNEL_ID = 1525906374628741192

SPAM_LIMIT = 3
SPAM_WINDOW = 3

MENTION_LIMIT = 4

INVITE_BLOCK = True
LINK_BLOCK = True
CAPS_BLOCK = True
RAID_LIMIT = 5
RAID_WINDOW = 10
CHANNEL_CREATE_LIMIT = 3
CHANNEL_CREATE_WINDOW = 10
ROLE_CREATE_LIMIT = 3
ROLE_CREATE_WINDOW = 10

# ==========================
# INTENTS
# ==========================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.messages = True
intents.voice_states = True
intents.guild_messages = True
intents.guild_reactions = True
intents.moderation = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

# ==========================
# DATABASE (TEMP)
# ==========================

warnings = defaultdict(lambda: {
    "count": 0,
    "reason": "لا يوجد"
})

spam = defaultdict(list)
mentions = defaultdict(list)
joins = defaultdict(list)
raid_joins = defaultdict(list)
channel_creates = defaultdict(list)
role_creates = defaultdict(list)
# ==========================
# READY
# ==========================

@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
    except Exception as e:
        print(e)

    print("=" * 40)
    print(f"Logged in as {bot.user}")
    print(f"Servers : {len(bot.guilds)}")
    print("Bot Ready ✅")
    print("=" * 40)
    # ==========================
# PUNISH SYSTEM
# ==========================

async def punish(member: discord.Member, reason: str = "Auto Moderation"):
    level = warnings[member.id]["count"]

    log_channel = bot.get_channel(LOG_CHANNEL_ID)

    punishment = "⚠️ تحذير"

    try:

        if level == 2:
            await member.timeout(
                datetime.timedelta(minutes=10),
                reason=reason
            )
            punishment = "🔇 ميوت 10 دقائق"

        elif level == 3:
            await member.timeout(
                datetime.timedelta(minutes=30),
                reason=reason
            )
            punishment = "🔇 ميوت 30 دقيقة"

        elif level == 4:
            await member.timeout(
                datetime.timedelta(hours=2),
                reason=reason
            )
            punishment = "🔇 ميوت ساعتين"

        elif level == 5:
            await member.timeout(
                datetime.timedelta(hours=4),
                reason=reason
            )
            punishment = "🔇 ميوت 4 ساعات"

        elif level == 6:
            await member.timeout(
                datetime.timedelta(hours=8),
                reason=reason
            )
            punishment = "🔇 ميوت 8 ساعات"

        elif level == 7:
            await member.kick(reason=reason)
            punishment = "👢 طرد"

        elif level >= 8:
            await member.ban(reason=reason)
            punishment = "🔨 باند"

        if log_channel:
            embed = discord.Embed(
                title="🚨 Auto Moderation",
                color=discord.Color.red(),
                timestamp=datetime.datetime.utcnow()
            )

            embed.add_field(
                name="👤 العضو",
                value=member.mention,
                inline=False
            )

            embed.add_field(
                name="📊 عدد التحذيرات",
                value=str(level),
                inline=True
            )

            embed.add_field(
                name="📌 العقوبة",
                value=punishment,
                inline=True
            )

            embed.add_field(
                name="📝 السبب",
                value=reason,
                inline=False
            )

            await log_channel.send(embed=embed)

    except discord.Forbidden:

        if log_channel:
            await log_channel.send(
                f"❌ لا أملك صلاحية معاقبة {member.mention}"
            )

    except Exception as e:
        print(e)
        # ==========================
# BYPASS SYSTEM
# ==========================

def is_protected(member: discord.Member) -> bool:
    """
    الأعضاء الذين لا تطبق عليهم أنظمة الحماية
    """

    # مالك السيرفر
    if member == member.guild.owner:
        return True

    perms = member.guild_permissions

    # أي شخص لديه صلاحيات إدارة
    if (
        perms.administrator
        or perms.manage_guild
        or perms.manage_messages
        or perms.manage_channels
        or perms.manage_roles
        or perms.kick_members
        or perms.ban_members
        or perms.moderate_members
    ):
        return True

    return False
    # ==========================
# MESSAGE EVENT
# ==========================

@bot.event
async def on_message(message: discord.Message):

    # تجاهل رسائل البوتات
    if message.author.bot:
        return

    # نتأكد أنها داخل سيرفر
    if not message.guild:
        return

    # تجاهل المالك والإدارة
    if is_protected(message.author):
        await bot.process_commands(message)
        return

    uid = message.author.id
    now = time.time()

    # ==========================
    # ANTI SPAM
    # ==========================

    spam[uid].append(now)

    spam[uid] = [
        t for t in spam[uid]
        if now - t < SPAM_WINDOW
    ]

    if len(spam[uid]) >= SPAM_LIMIT:

        try:
            await message.delete()
        except:
            pass

        warnings[uid]["count"] += 1
        warnings[uid]["reason"] = "Spam"

        await punish(
            message.author,
            "Spam"
        )

        try:
            await message.channel.send(
                f"🚫 {message.author.mention} يمنع السبام.",
                delete_after=5
            )
        except:
            pass

        return

        # ==========================
    # ANTI MENTION SPAM
    # ==========================

    if len(message.mentions) >= MENTION_LIMIT:

        try:
            await message.delete()
        except:
            pass

        warnings[uid]["count"] += 1
        warnings[uid]["reason"] = "Mention Spam"

        await punish(
            message.author,
            "Mention Spam"
        )

        try:
            await message.channel.send(
                f"🚫 {message.author.mention} يمنع المنشن الجماعي.",
                delete_after=5
            )
        except:
            pass

        return
            # ==========================
    # ANTI LINKS
    # ==========================

    if LINK_BLOCK:

        content = message.content.lower()

        # روابط الديسكورد ممنوعة دائمًا
        discord_invites = (
            "discord.gg/",
            "discord.com/invite/",
            "discordapp.com/invite/"
        )

        # المواقع المسموح بها
        allowed_domains = (
            "youtube.com",
            "youtu.be",
            "google.com",
            "github.com",
            "instagram.com",
            "tiktok.com",
            "facebook.com",
            "x.com",
            "twitter.com",
        )

        # منع دعوات الديسكورد
        if any(invite in content for invite in discord_invites):

            try:
                await message.delete()
            except:
                pass

            warnings[uid]["count"] += 1
            warnings[uid]["reason"] = "Discord Invite"

            await punish(message.author, "Discord Invite")

            await message.channel.send(
                f"🚫 {message.author.mention} يمنع نشر دعوات الديسكورد.",
                delete_after=5
            )

            return

        # التحقق من الروابط الأخرى
        if "http://" in content or "https://" in content or "www." in content:

            if not any(domain in content for domain in allowed_domains):

                try:
                    await message.delete()
                except:
                    pass

                warnings[uid]["count"] += 1
                warnings[uid]["reason"] = "Unknown Link"

                await punish(message.author, "Unknown Link")

                await message.channel.send(
                    f"🚫 {message.author.mention} هذا الرابط غير مسموح.",
                    delete_after=5
                )

                return
                    # ==========================
    # ANTI CAPS
    # ==========================

    if CAPS_BLOCK:

        text = message.content.strip()

        # تجاهل الرسائل القصيرة
        if len(text) >= 8:

            letters = [c for c in text if c.isalpha()]

            if letters:

                uppercase = sum(c.isupper() for c in letters)

                percentage = uppercase / len(letters)

                # إذا كانت أكثر من 80% من الأحرف كبيرة
                if percentage >= 0.80:

                    try:
                        await message.delete()
                    except:
                        pass

                    warnings[uid]["count"] += 1
                    warnings[uid]["reason"] = "Caps Spam"

                    await punish(
                        message.author,
                        "Caps Spam"
                    )

                    try:
                        await message.channel.send(
                            f"🚫 {message.author.mention} يرجى عدم الكتابة بالأحرف الكبيرة فقط.",
                            delete_after=5
                        )
                    except:
                        pass

                    return

    await bot.process_commands(message)
    # ==========================
# ANTI RAID
# ==========================

@bot.event
async def on_member_join(member: discord.Member):

    if is_protected(member):
        return

    now = time.time()

    raid_joins[member.guild.id].append(now)

    raid_joins[member.guild.id] = [
        t for t in raid_joins[member.guild.id]
        if now - t < RAID_WINDOW
    ]

    if len(raid_joins[member.guild.id]) >= RAID_LIMIT:

        log = bot.get_channel(LOG_CHANNEL_ID)

        if log:
            embed = discord.Embed(
                title="🚨 تم اكتشاف Raid",
                description=(
                    f"دخل **{len(raid_joins[member.guild.id])}** أعضاء "
                    f"خلال **{RAID_WINDOW}** ثوانٍ."
                ),
                color=discord.Color.red(),
                timestamp=datetime.datetime.utcnow()
            )

            await log.send(embed=embed)
            # ==========================
# ANTI NUKE
# ==========================

@bot.event
async def on_guild_channel_delete(channel):

    try:
        async for entry in channel.guild.audit_logs(
            limit=1,
            action=discord.AuditLogAction.channel_delete
        ):

            user = entry.user

            if user is None:
                return

            # تجاهل المالك
            if user.id == channel.guild.owner_id:
                return

            # تجاهل الإدارة
            member = channel.guild.get_member(user.id)

            if member and is_protected(member):
                return

            await channel.guild.ban(
                user,
                reason="Anti Nuke | Channel Delete"
            )

            log = bot.get_channel(LOG_CHANNEL_ID)

            if log:
                await log.send(
                    f"🚨 تم حظر {user.mention} بسبب حذف روم."
                )

            break

    except Exception as e:
        print(e)

        # ==========================
# VOICE MUTE
# ==========================

@bot.tree.command(
    name="vmute",
    description="كتم عضو في الروم الصوتي"
)
async def vmute(
    interaction: discord.Interaction,
    member: discord.Member
):

    # التحقق من الصلاحيات
    if not interaction.user.guild_permissions.moderate_members:
        return await interaction.response.send_message(
            "❌ ليس لديك صلاحية.",
            ephemeral=True
        )

    # تجاهل المالك والإدارة
    if is_protected(member):
        return await interaction.response.send_message(
            "❌ لا يمكن كتم الإدارة أو مالك السيرفر.",
            ephemeral=True
        )

    # يجب أن يكون العضو داخل روم صوتي
    if member.voice is None:
        return await interaction.response.send_message(
            "❌ العضو ليس داخل روم صوتي.",
            ephemeral=True
        )

    try:

        await member.edit(
            mute=True,
            reason=f"Voice Mute | {interaction.user}"
        )

        await interaction.response.send_message(
            f"🔇 تم كتم {member.mention} في الروم الصوتي."
        )

        log = bot.get_channel(LOG_CHANNEL_ID)

        if log:
            await log.send(
                f"🔇 {interaction.user.mention} قام بكتم {member.mention} في الفويس."
            )

    except Exception as e:
        await interaction.response.send_message(
            f"❌ {e}",
            ephemeral=True
        )
        # ==========================
# VOICE UNMUTE
# ==========================

@bot.tree.command(
    name="vunmute",
    description="فك كتم عضو في الروم الصوتي"
)
async def vunmute(
    interaction: discord.Interaction,
    member: discord.Member
):

    if not interaction.user.guild_permissions.moderate_members:
        return await interaction.response.send_message(
            "❌ ليس لديك صلاحية.",
            ephemeral=True
        )

    if member.voice is None:
        return await interaction.response.send_message(
            "❌ العضو ليس داخل روم صوتي.",
            ephemeral=True
        )

    try:

        await member.edit(
            mute=False,
            reason=f"Voice Unmute | {interaction.user}"
        )

        await interaction.response.send_message(
            f"🔊 تم فك كتم {member.mention}."
        )

        log = bot.get_channel(LOG_CHANNEL_ID)

        if log:
            await log.send(
                f"🔊 {interaction.user.mention} قام بفك كتم {member.mention}."
            )

    except Exception as e:
        await interaction.response.send_message(
            f"❌ {e}",
            ephemeral=True
        )
        # ==========================
# VOICE MUTE ALL
# ==========================

@bot.tree.command(
    name="vmuteall",
    description="كتم جميع أعضاء الرومات الصوتية"
)
async def vmuteall(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.moderate_members:
        return await interaction.response.send_message(
            "❌ ليس لديك صلاحية.",
            ephemeral=True
        )

    muted = 0

    for member in interaction.guild.members:

        if member.voice is None:
            continue

        if is_protected(member):
            continue

        try:
            await member.edit(
                mute=True,
                reason=f"Voice Mute All | {interaction.user}"
            )
            muted += 1

        except Exception:
            pass

    await interaction.response.send_message(
        f"🔇 تم كتم **{muted}** عضو في الرومات الصوتية."
    )

    log = bot.get_channel(LOG_CHANNEL_ID)

    if log:
        await log.send(
            f"🔇 {interaction.user.mention} استخدم أمر Voice Mute All.\n"
            f"عدد الأعضاء: **{muted}**"
        )
        # ==========================
# VOICE UNMUTE ALL
# ==========================

@bot.tree.command(
    name="vunmuteall",
    description="فك كتم جميع أعضاء الرومات الصوتية"
)
async def vunmuteall(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.moderate_members:
        return await interaction.response.send_message(
            "❌ ليس لديك صلاحية.",
            ephemeral=True
        )

    unmuted = 0

    for member in interaction.guild.members:

        if member.voice is None:
            continue

        if is_protected(member):
            continue

        try:
            await member.edit(
                mute=False,
                reason=f"Voice Unmute All | {interaction.user}"
            )
            unmuted += 1

        except Exception:
            pass

    await interaction.response.send_message(
        f"🔊 تم فك كتم **{unmuted}** عضو في الرومات الصوتية."
    )

    log = bot.get_channel(LOG_CHANNEL_ID)

    if log:
        await log.send(
            f"🔊 {interaction.user.mention} استخدم أمر Voice Unmute All.\n"
            f"عدد الأعضاء: **{unmuted}**"
        )
        # ==========================
# BAN
# ==========================

@bot.tree.command(
    name="ban",
    description="حظر عضو من السيرفر"
)
async def ban(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str = "No Reason"
):

    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message(
            "❌ ليس لديك صلاحية.",
            ephemeral=True
        )

    # لا يمكن حظر المالك أو الإدارة
    if is_protected(member):
        return await interaction.response.send_message(
            "❌ لا يمكن حظر الإدارة أو مالك السيرفر.",
            ephemeral=True
        )

    # لا يمكن حظر نفسك
    if member == interaction.user:
        return await interaction.response.send_message(
            "❌ لا يمكنك حظر نفسك.",
            ephemeral=True
        )

    try:

        await member.ban(
            reason=f"{reason} | By {interaction.user}"
        )

        await interaction.response.send_message(
            f"🔨 تم حظر {member.mention}\n📌 السبب: {reason}"
        )

        log = bot.get_channel(LOG_CHANNEL_ID)

        if log:
            embed = discord.Embed(
                title="🔨 Ban",
                color=discord.Color.red(),
                timestamp=datetime.datetime.utcnow()
            )

            embed.add_field(
                name="العضو",
                value=member.mention,
                inline=False
            )

            embed.add_field(
                name="بواسطة",
                value=interaction.user.mention,
                inline=False
            )

            embed.add_field(
                name="السبب",
                value=reason,
                inline=False
            )

            await log.send(embed=embed)

    except Exception as e:
        await interaction.response.send_message(
            f"❌ {e}",
            ephemeral=True
        )
        # ==========================
# UNBAN
# ==========================

@bot.tree.command(
    name="unban",
    description="إلغاء حظر عضو"
)
async def unban(
    interaction: discord.Interaction,
    user_id: str
):

    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message(
            "❌ ليس لديك صلاحية.",
            ephemeral=True
        )

    try:

        user = await bot.fetch_user(int(user_id))

        await interaction.guild.unban(
            user,
            reason=f"By {interaction.user}"
        )

        await interaction.response.send_message(
            f"✅ تم إلغاء حظر **{user}**"
        )

        log = bot.get_channel(LOG_CHANNEL_ID)

        if log:
            await log.send(
                f"✅ {interaction.user.mention} ألغى حظر **{user}**"
            )

    except Exception as e:
        await interaction.response.send_message(
            f"❌ {e}",
            ephemeral=True
        )
        # ==========================
# KICK
# ==========================

@bot.tree.command(
    name="kick",
    description="طرد عضو من السيرفر"
)
async def kick(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str = "No Reason"
):

    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message(
            "❌ ليس لديك صلاحية.",
            ephemeral=True
        )

    # لا يمكن طرد نفسك
    if member == interaction.user:
        return await interaction.response.send_message(
            "❌ لا يمكنك طرد نفسك.",
            ephemeral=True
        )

    # لا يمكن طرد المالك أو الإدارة
    if is_protected(member):
        return await interaction.response.send_message(
            "❌ لا يمكن طرد الإدارة أو مالك السيرفر.",
            ephemeral=True
        )

    # لا يمكن طرد شخص رتبته أعلى أو مساوية لك
    if member.top_role >= interaction.user.top_role:
        return await interaction.response.send_message(
            "❌ لا يمكنك طرد عضو رتبته أعلى أو مساوية لرتبتك.",
            ephemeral=True
        )

    # لا يمكن للبوت طرد شخص أعلى منه
    if member.top_role >= interaction.guild.me.top_role:
        return await interaction.response.send_message(
            "❌ رتبة العضو أعلى من رتبة البوت.",
            ephemeral=True
        )

    try:

        await member.kick(
            reason=f"{reason} | By {interaction.user}"
        )

        await interaction.response.send_message(
            f"👢 تم طرد {member.mention}\n📌 السبب: {reason}"
        )

        log = bot.get_channel(LOG_CHANNEL_ID)

        if log:
            embed = discord.Embed(
                title="👢 Kick",
                color=discord.Color.orange(),
                timestamp=datetime.datetime.utcnow()
            )

            embed.add_field(
                name="العضو",
                value=member.mention,
                inline=False
            )

            embed.add_field(
                name="بواسطة",
                value=interaction.user.mention,
                inline=False
            )

            embed.add_field(
                name="السبب",
                value=reason,
                inline=False
            )

            await log.send(embed=embed)

    except Exception as e:
        await interaction.response.send_message(
            f"❌ {e}",
            ephemeral=True
        )
        # ==========================
# CLEAR
# ==========================

@bot.tree.command(
    name="clear",
    description="حذف عدد من الرسائل"
)
async def clear(
    interaction: discord.Interaction,
    amount: int
):

    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message(
            "❌ ليس لديك صلاحية.",
            ephemeral=True
        )

    # الحد الأدنى والأقصى
    if amount < 1:
        return await interaction.response.send_message(
            "❌ العدد يجب أن يكون أكبر من 0.",
            ephemeral=True
        )

    if amount > 100:
        return await interaction.response.send_message(
            "❌ الحد الأقصى هو 100 رسالة.",
            ephemeral=True
        )

    await interaction.response.defer(ephemeral=True)

    deleted = await interaction.channel.purge(limit=amount)

    await interaction.followup.send(
        f"🧹 تم حذف **{len(deleted)}** رسالة.",
        ephemeral=True
    )

    log = bot.get_channel(LOG_CHANNEL_ID)

    if log:
        embed = discord.Embed(
            title="🧹 Clear",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.utcnow()
        )

        embed.add_field(
            name="المشرف",
            value=interaction.user.mention,
            inline=False
        )

        embed.add_field(
            name="القناة",
            value=interaction.channel.mention,
            inline=False
        )

        embed.add_field(
            name="عدد الرسائل",
            value=str(len(deleted)),
            inline=False
        )

        await log.send(embed=embed)
        # ==========================
# TIMEOUT
# ==========================

@bot.tree.command(
    name="timeout",
    description="إعطاء تايم أوت لعضو"
)
async def timeout(
    interaction: discord.Interaction,
    member: discord.Member,
    minutes: int,
    reason: str = "No Reason"
):

    if not interaction.user.guild_permissions.moderate_members:
        return await interaction.response.send_message(
            "❌ ليس لديك صلاحية.",
            ephemeral=True
        )

    if is_protected(member):
        return await interaction.response.send_message(
            "❌ لا يمكن معاقبة الإدارة أو مالك السيرفر.",
            ephemeral=True
        )

    if member == interaction.user:
        return await interaction.response.send_message(
            "❌ لا يمكنك إعطاء نفسك Timeout.",
            ephemeral=True
        )

    if member.top_role >= interaction.user.top_role:
        return await interaction.response.send_message(
            "❌ لا يمكنك معاقبة عضو رتبته أعلى أو مساوية لرتبتك.",
            ephemeral=True
        )

    if member.top_role >= interaction.guild.me.top_role:
        return await interaction.response.send_message(
            "❌ رتبة العضو أعلى من رتبة البوت.",
            ephemeral=True
        )

    try:

        await member.timeout(
            datetime.timedelta(minutes=minutes),
            reason=f"{reason} | By {interaction.user}"
        )

        await interaction.response.send_message(
            f"⏳ تم إعطاء {member.mention} Timeout لمدة **{minutes}** دقيقة.\n"
            f"📌 السبب: {reason}"
        )

        log = bot.get_channel(LOG_CHANNEL_ID)

        if log:
            embed = discord.Embed(
                title="⏳ Timeout",
                color=discord.Color.gold(),
                timestamp=datetime.datetime.utcnow()
            )

            embed.add_field(
                name="العضو",
                value=member.mention,
                inline=False
            )

            embed.add_field(
                name="المدة",
                value=f"{minutes} دقيقة",
                inline=False
            )

            embed.add_field(
                name="السبب",
                value=reason,
                inline=False
            )

            embed.add_field(
                name="بواسطة",
                value=interaction.user.mention,
                inline=False
            )

            await log.send(embed=embed)

    except Exception as e:
        await interaction.response.send_message(
            f"❌ {e}",
            ephemeral=True
        )
        # ==========================
# UNTIMEOUT
# ==========================

@bot.tree.command(
    name="untimeout",
    description="إزالة التايم أوت عن عضو"
)
async def untimeout(
    interaction: discord.Interaction,
    member: discord.Member
):

    if not interaction.user.guild_permissions.moderate_members:
        return await interaction.response.send_message(
            "❌ ليس لديك صلاحية.",
            ephemeral=True
        )

    if member.top_role >= interaction.user.top_role:
        return await interaction.response.send_message(
            "❌ لا يمكنك إزالة التايم أوت عن عضو رتبته أعلى أو مساوية لرتبتك.",
            ephemeral=True
        )

    if member.top_role >= interaction.guild.me.top_role:
        return await interaction.response.send_message(
            "❌ رتبة العضو أعلى من رتبة البوت.",
            ephemeral=True
        )

    try:
        await member.edit(
            timed_out_until=None,
            reason=f"Untimeout | By {interaction.user}"
        )

        await interaction.response.send_message(
            f"✅ تم إزالة التايم أوت عن {member.mention}."
        )

        log = bot.get_channel(LOG_CHANNEL_ID)

        if log:
            embed = discord.Embed(
                title="✅ Untimeout",
                color=discord.Color.green(),
                timestamp=datetime.datetime.utcnow()
            )

            embed.add_field(
                name="العضو",
                value=member.mention,
                inline=False
            )

            embed.add_field(
                name="بواسطة",
                value=interaction.user.mention,
                inline=False
            )

            await log.send(embed=embed)

    except Exception as e:
        await interaction.response.send_message(
            f"❌ {e}",
            ephemeral=True
        )
        # ==========================
# USER INFO
# ==========================

@bot.tree.command(
    name="userinfo",
    description="عرض معلومات عضو"
)
async def userinfo(
    interaction: discord.Interaction,
    member: discord.Member = None
):

    member = member or interaction.user

    embed = discord.Embed(
        title="👤 معلومات العضو",
        color=discord.Color.blurple(),
        timestamp=datetime.datetime.utcnow()
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    embed.add_field(
        name="👤 الاسم",
        value=member.name,
        inline=True
    )

    embed.add_field(
        name="📝 الاسم المعروض",
        value=member.display_name,
        inline=True
    )

    embed.add_field(
        name="🆔 ID",
        value=member.id,
        inline=False
    )

    embed.add_field(
        name="📅 إنشاء الحساب",
        value=f"<t:{int(member.created_at.timestamp())}:F>",
        inline=False
    )

    embed.add_field(
        name="📥 دخول السيرفر",
        value=f"<t:{int(member.joined_at.timestamp())}:F>",
        inline=False
    )

    embed.add_field(
        name="🎭 أعلى رتبة",
        value=member.top_role.mention,
        inline=False
    )

    embed.add_field(
        name="🤖 بوت؟",
        value="✅ نعم" if member.bot else "❌ لا",
        inline=True
    )

    embed.add_field(
        name="⚠️ التحذيرات",
        value=str(warnings[member.id]["count"]),
        inline=True
    )

    await interaction.response.send_message(embed=embed)
    # ==========================
# SERVER INFO
# ==========================

@bot.tree.command(
    name="serverinfo",
    description="عرض معلومات السيرفر"
)
async def serverinfo(interaction: discord.Interaction):

    guild = interaction.guild

    humans = sum(not m.bot for m in guild.members)
    bots = sum(m.bot for m in guild.members)

    embed = discord.Embed(
        title=f"🏠 معلومات السيرفر | {guild.name}",
        color=discord.Color.blue(),
        timestamp=datetime.datetime.utcnow()
    )

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    embed.add_field(
        name="👑 المالك",
        value=f"<@{guild.owner_id}>",
        inline=True
    )

    embed.add_field(
        name="🆔 ID",
        value=str(guild.id),
        inline=True
    )

    embed.add_field(
        name="📅 تاريخ الإنشاء",
        value=f"<t:{int(guild.created_at.timestamp())}:F>",
        inline=False
    )

    embed.add_field(
        name="👥 الأعضاء",
        value=f"الإجمالي: {guild.member_count}\nالأعضاء: {humans}\nالبوتات: {bots}",
        inline=False
    )

    embed.add_field(
        name="💬 الرومات",
        value=f"📁 الفئات: {len(guild.categories)}\n📝 النصية: {len(guild.text_channels)}\n🔊 الصوتية: {len(guild.voice_channels)}",
        inline=False
    )

    embed.add_field(
        name="🎭 الرتب",
        value=str(len(guild.roles)),
        inline=True
    )

    embed.add_field(
        name="😀 الإيموجيات",
        value=str(len(guild.emojis)),
        inline=True
    )

    embed.add_field(
        name="🚀 مستوى البوست",
        value=f"Level {guild.premium_tier}",
        inline=True
    )

    await interaction.response.send_message(embed=embed)
    # ==========================
# AVATAR
# ==========================

@bot.tree.command(
    name="avatar",
    description="عرض صورة عضو"
)
async def avatar(
    interaction: discord.Interaction,
    member: discord.Member = None
):

    member = member or interaction.user

    embed = discord.Embed(
        title=f"🖼️ صورة {member.display_name}",
        color=discord.Color.blurple(),
        timestamp=datetime.datetime.utcnow()
    )

    embed.set_image(url=member.display_avatar.url)

    embed.set_footer(
        text=f"Requested by {interaction.user}",
        icon_url=interaction.user.display_avatar.url
    )

    await interaction.response.send_message(embed=embed)
    # ==========================
# ROLE INFO
# ==========================

@bot.tree.command(
    name="roleinfo",
    description="عرض معلومات رتبة"
)
async def roleinfo(
    interaction: discord.Interaction,
    role: discord.Role
):

    embed = discord.Embed(
        title=f"🎭 معلومات الرتبة | {role.name}",
        color=role.color if role.color.value != 0 else discord.Color.blurple(),
        timestamp=datetime.datetime.utcnow()
    )

    embed.add_field(
        name="📛 الاسم",
        value=role.name,
        inline=True
    )

    embed.add_field(
        name="🆔 ID",
        value=role.id,
        inline=True
    )

    embed.add_field(
        name="👥 عدد الأعضاء",
        value=len(role.members),
        inline=True
    )

    embed.add_field(
        name="📈 الموقع",
        value=role.position,
        inline=True
    )

    embed.add_field(
        name="🎨 اللون",
        value=str(role.color),
        inline=True
    )

    embed.add_field(
        name="🤖 تدار بواسطة بوت",
        value="✅ نعم" if role.managed else "❌ لا",
        inline=True
    )

    embed.add_field(
        name="📅 تاريخ الإنشاء",
        value=f"<t:{int(role.created_at.timestamp())}:F>",
        inline=False
    )

    await interaction.response.send_message(embed=embed)
    # ==========================
# LOCK CHANNEL
# ==========================

@bot.tree.command(
    name="lock",
    description="قفل الروم الحالي"
)
async def lock(
    interaction: discord.Interaction,
    reason: str = "No Reason"
):

    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message(
            "❌ ليس لديك صلاحية.",
            ephemeral=True
        )

    channel = interaction.channel

    overwrite = channel.overwrites_for(interaction.guild.default_role)
    overwrite.send_messages = False

    await channel.set_permissions(
        interaction.guild.default_role,
        overwrite=overwrite,
        reason=f"{reason} | By {interaction.user}"
    )

    embed = discord.Embed(
        title="🔒 تم قفل الروم",
        description=f"**السبب:** {reason}",
        color=discord.Color.red(),
        timestamp=datetime.datetime.utcnow()
    )

    embed.set_footer(
        text=f"بواسطة {interaction.user}",
        icon_url=interaction.user.display_avatar.url
    )

    await interaction.response.send_message(embed=embed)

    log = bot.get_channel(LOG_CHANNEL_ID)

    if log:
        await log.send(
            f"🔒 {interaction.user.mention} قام بقفل {channel.mention}\n"
            f"📌 السبب: {reason}"
        )
        # ==========================
# UNLOCK CHANNEL
# ==========================

@bot.tree.command(
    name="unlock",
    description="فتح الروم الحالي"
)
async def unlock(
    interaction: discord.Interaction
):

    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message(
            "❌ ليس لديك صلاحية.",
            ephemeral=True
        )

    channel = interaction.channel

    overwrite = channel.overwrites_for(interaction.guild.default_role)
    overwrite.send_messages = None

    await channel.set_permissions(
        interaction.guild.default_role,
        overwrite=overwrite,
        reason=f"Unlocked by {interaction.user}"
    )

    embed = discord.Embed(
        title="🔓 تم فتح الروم",
        color=discord.Color.green(),
        timestamp=datetime.datetime.utcnow()
    )

    embed.set_footer(
        text=f"بواسطة {interaction.user}",
        icon_url=interaction.user.display_avatar.url
    )

    await interaction.response.send_message(embed=embed)

    log = bot.get_channel(LOG_CHANNEL_ID)

    if log:
        await log.send(
            f"🔓 {interaction.user.mention} قام بفتح {channel.mention}"
        )
        # ==========================
# SLOWMODE
# ==========================

@bot.tree.command(
    name="slowmode",
    description="تغيير مدة السلو مود للروم الحالي"
)
async def slowmode(
    interaction: discord.Interaction,
    seconds: int
):

    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message(
            "❌ ليس لديك صلاحية.",
            ephemeral=True
        )

    if seconds < 0 or seconds > 21600:
        return await interaction.response.send_message(
            "❌ المدة يجب أن تكون بين 0 و 21600 ثانية (6 ساعات).",
            ephemeral=True
        )

    try:
        await interaction.channel.edit(
            slowmode_delay=seconds,
            reason=f"By {interaction.user}"
        )

        if seconds == 0:
            embed = discord.Embed(
                title="🐌 تم إيقاف السلو مود",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="🐌 تم تغيير السلو مود",
                description=f"المدة: **{seconds}** ثانية",
                color=discord.Color.orange()
            )

        embed.timestamp = datetime.datetime.utcnow()

        await interaction.response.send_message(embed=embed)

        log = bot.get_channel(LOG_CHANNEL_ID)

        if log:
            await log.send(
                f"🐌 {interaction.user.mention} غيّر السلو مود في {interaction.channel.mention} إلى **{seconds}** ثانية."
            )

    except Exception as e:
        await interaction.response.send_message(
            f"❌ {e}",
            ephemeral=True
        )
        # ==========================
# ADD ROLE
# ==========================

@bot.tree.command(
    name="addrole",
    description="إعطاء رتبة لعضو"
)
async def addrole(
    interaction: discord.Interaction,
    member: discord.Member,
    role: discord.Role
):

    if not interaction.user.guild_permissions.manage_roles:
        return await interaction.response.send_message(
            "❌ ليس لديك صلاحية.",
            ephemeral=True
        )

    # منع إعطاء رتب أعلى من رتبة المنفذ
    if role >= interaction.user.top_role:
        return await interaction.response.send_message(
            "❌ لا يمكنك إعطاء رتبة أعلى أو مساوية لرتبتك.",
            ephemeral=True
        )

    # منع البوت من التعامل مع رتب أعلى منه
    if role >= interaction.guild.me.top_role:
        return await interaction.response.send_message(
            "❌ رتبة البوت يجب أن تكون أعلى من هذه الرتبة.",
            ephemeral=True
        )

    try:
        await member.add_roles(
            role,
            reason=f"By {interaction.user}"
        )

        embed = discord.Embed(
            title="✅ تمت إضافة الرتبة",
            color=discord.Color.green(),
            timestamp=datetime.datetime.utcnow()
        )

        embed.add_field(
            name="👤 العضو",
            value=member.mention,
            inline=False
        )

        embed.add_field(
            name="🎭 الرتبة",
            value=role.mention,
            inline=False
        )

        embed.add_field(
            name="🛡️ بواسطة",
            value=interaction.user.mention,
            inline=False
        )

        await interaction.response.send_message(embed=embed)

        log = bot.get_channel(LOG_CHANNEL_ID)

        if log:
            await log.send(
                f"✅ {interaction.user.mention} أعطى رتبة {role.mention} إلى {member.mention}"
            )

    except Exception as e:
        await interaction.response.send_message(
            f"❌ {e}",
            ephemeral=True
        )
        # ==========================
# REMOVE ROLE
# ==========================

@bot.tree.command(
    name="removerole",
    description="إزالة رتبة من عضو"
)
async def removerole(
    interaction: discord.Interaction,
    member: discord.Member,
    role: discord.Role
):

    if not interaction.user.guild_permissions.manage_roles:
        return await interaction.response.send_message(
            "❌ ليس لديك صلاحية.",
            ephemeral=True
        )

    if role >= interaction.user.top_role:
        return await interaction.response.send_message(
            "❌ لا يمكنك إزالة رتبة أعلى أو مساوية لرتبتك.",
            ephemeral=True
        )

    if role >= interaction.guild.me.top_role:
        return await interaction.response.send_message(
            "❌ رتبة البوت يجب أن تكون أعلى من هذه الرتبة.",
            ephemeral=True
        )

    try:

        await member.remove_roles(
            role,
            reason=f"By {interaction.user}"
        )

        embed = discord.Embed(
            title="❌ تمت إزالة الرتبة",
            color=discord.Color.red(),
            timestamp=datetime.datetime.utcnow()
        )

        embed.add_field(
            name="👤 العضو",
            value=member.mention,
            inline=False
        )

        embed.add_field(
            name="🎭 الرتبة",
            value=role.mention,
            inline=False
        )

        embed.add_field(
            name="🛡️ بواسطة",
            value=interaction.user.mention,
            inline=False
        )

        await interaction.response.send_message(embed=embed)

        log = bot.get_channel(LOG_CHANNEL_ID)

        if log:
            await log.send(
                f"❌ {interaction.user.mention} أزال رتبة {role.mention} من {member.mention}"
            )

    except Exception as e:
        await interaction.response.send_message(
            f"❌ {e}",
            ephemeral=True
        )
        # ==========================
# NICKNAME
# ==========================

@bot.tree.command(
    name="nickname",
    description="تغيير لقب عضو"
)
async def nickname(
    interaction: discord.Interaction,
    member: discord.Member,
    nickname: str = None
):

    if not interaction.user.guild_permissions.manage_nicknames:
        return await interaction.response.send_message(
            "❌ ليس لديك صلاحية.",
            ephemeral=True
        )

    # تجاهل الإدارة والمالك
    if is_protected(member):
        return await interaction.response.send_message(
            "❌ لا يمكن تغيير لقب الإدارة أو مالك السيرفر.",
            ephemeral=True
        )

    # لا يمكن تعديل عضو أعلى رتبة
    if member.top_role >= interaction.user.top_role:
        return await interaction.response.send_message(
            "❌ لا يمكنك تعديل عضو رتبته أعلى أو مساوية لرتبتك.",
            ephemeral=True
        )

    # يجب أن تكون رتبة البوت أعلى
    if member.top_role >= interaction.guild.me.top_role:
        return await interaction.response.send_message(
            "❌ رتبة البوت أقل من رتبة العضو.",
            ephemeral=True
        )

    try:
        await member.edit(
            nick=nickname,
            reason=f"By {interaction.user}"
        )

        embed = discord.Embed(
            title="✏️ تم تغيير اللقب",
            color=discord.Color.blurple(),
            timestamp=datetime.datetime.utcnow()
        )

        embed.add_field(
            name="👤 العضو",
            value=member.mention,
            inline=False
        )

        embed.add_field(
            name="📝 اللقب الجديد",
            value=nickname if nickname else "تمت إزالة اللقب",
            inline=False
        )

        embed.add_field(
            name="🛡️ بواسطة",
            value=interaction.user.mention,
            inline=False
        )

        await interaction.response.send_message(embed=embed)

        log = bot.get_channel(LOG_CHANNEL_ID)

        if log:
            await log.send(embed=embed)

    except Exception as e:
        await interaction.response.send_message(
            f"❌ {e}",
            ephemeral=True
        )
                # ==========================
# warns
# ==========================
        @bot.tree.command(
    name="warns",
    description="عرض تحذيرات عضو"
)
async def warns(
    interaction: discord.Interaction,
    member: discord.Member = None
):

    member = member or interaction.user

    data = warnings[member.id]

    await interaction.response.send_message(
        f"👤 العضو: {member.mention}\n"
        f"⚠️ التحذيرات: **{data['count']}**\n"
        f"📝 آخر سبب: **{data['reason']}**"
    )
            # ==========================
# clearwarns
# ==========================
@bot.tree.command(
    name="clearwarns",
    description="حذف جميع تحذيرات عضو"
)
async def clearwarns(
    interaction: discord.Interaction,
    member: discord.Member
):

    if not interaction.user.guild_permissions.moderate_members:
        return await interaction.response.send_message(
            "❌ ليس لديك صلاحية.",
            ephemeral=True
        )

    warnings[member.id] = {
        "count": 0,
        "reason": "لا يوجد"
    }

    await interaction.response.send_message(
        f"✅ تم حذف جميع تحذيرات {member.mention}."
    )

    log = bot.get_channel(LOG_CHANNEL_ID)

    if log:
        await log.send(
            f"🧹 {interaction.user.mention} حذف جميع تحذيرات {member.mention}."
        )

        print("=" * 40)
print("TOKEN:", TOKEN)
print("=" * 40)

bot.run(TOKEN)
