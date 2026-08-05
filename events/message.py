# ==========================
# AI Moderation
# ==========================

safe = await check_message(message.content)

if not safe:

    try:
        await message.delete()
    except discord.Forbidden:
        pass

    # إذا كان مالك السيرفر أو Administrator
    if (
        message.author == message.guild.owner
        or message.author.guild_permissions.administrator
    ):

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
        value=message.author.mention,
        inline=False
    )

    embed.add_field(
        name="💬 Message",
        value=f"```{message.content[:1000]}```",
        inline=False
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
