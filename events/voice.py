import discord
from discord.ext import commands


class VoiceEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        # إذا دخل روم صوتي وكان عليه Server Mute
        if before.channel is None and after.channel is not None:
            if after.mute:
                try:
                    await member.edit(
                        mute=False,
                        reason="Auto unmute when rejoining voice"
                    )
                except (discord.Forbidden, discord.HTTPException):
                    pass


async def setup(bot):
    await bot.add_cog(VoiceEvents(bot))
