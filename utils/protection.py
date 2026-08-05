import discord


def is_protected(member: discord.Member):

    return (
        member == member.guild.owner
        or member.guild_permissions.administrator
    )
