import discord
from discord.ext import commands


class VoiceEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        # إذا كان الشخص خرج من روم صوتي وكان عليه Server Mute
        if before.channel is not None and after.channel is None:
            if member.voice and member.voice.mute:
                try:
                    await member.edit(mute=False, reason="Left voice channel")
                except discord.Forbidden:
                    pass
                except discord.HTTPException:
                    pass


async def setup(bot):
    await bot.add_cog(VoiceEvents(bot))
