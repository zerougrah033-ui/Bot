import discord
from datetime import timedelta

from database.database import add_warning, get_warnings


async def punish(member: discord.Member, reason: str):
    guild = member.guild

    # إضافة تحذير
    add_warning(guild.id, member.id)
    warns = get_warnings(guild.id, member.id)

    # العقوبات
    if warns == 1:
        await member.timeout(
            timedelta(minutes=30),
            reason=reason
        )

    elif warns == 2:
        await member.timeout(
            timedelta(hours=1),
            reason=reason
        )

    elif warns == 3:
        await member.timeout(
            timedelta(hours=3),
            reason=reason
        )

    elif warns == 4:
        await member.timeout(
            timedelta(hours=6),
            reason=reason
        )

    elif warns == 5:
        await member.timeout(
            timedelta(hours=12),
            reason=reason
        )

    elif warns == 6:
        await member.timeout(
            timedelta(days=1),
            reason=reason
        )

    elif warns == 7:
        await member.timeout(
            timedelta(days=3),
            reason=reason
        )

    elif warns == 8:
        await member.kick(reason=reason)

    elif warns >= 9:
        await member.ban(reason=reason)

    return warns
