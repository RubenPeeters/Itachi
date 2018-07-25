import discord

async def get_feedbackchannel(self):
    for x in self.bot.guilds:
        if x.id == 457833113771442201:
            feedback_channel = discord.utils.get(x.channels, id=468338554532134922)
    return feedback_channel