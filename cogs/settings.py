import discord
import discord.ext.commands as commands
import json

def setup(bot):
    bot.add_cog(settings(bot))

class settings:
    def __init__(self, bot):
        self.bot = bot

    async def update_data_update(self, settings, channel):
        if str(channel.guild.id) not in settings:
            settings[str(channel.guild.id)] = {}
            settings[str(channel.guild.id)]["update"] = channel.id
        else:
            settings[str(channel.guild.id)]["update"] = channel.id
        await channel.send("The update channel has been set to this channel.")

    async def update_data_mod(self, settings, channel):
        if str(channel.guild.id) not in settings:
            settings[str(channel.guild.id)] = {}
            settings[str(channel.guild.id)]["mod"] = channel.id
        else:
            settings[str(channel.guild.id)]["mod"] = channel.id
        await channel.send("The mod channel has been set to this channel.")

    @commands.command(aliases=["setu"])
    @commands.has_permissions(administrator=True)
    async def setupdatechannel(self, ctx, *, channel: discord.TextChannel):
        with open('settings.json', 'r') as f:
            settings = json.load(f)
        await self.update_data_update(settings, channel)
        with open('settings.json', 'w') as f:
            json.dump(settings, f)

    @commands.command(aliases=["setm"])
    @commands.has_permissions(administrator=True)
    async def setmodchannel(self, ctx, *, channel: discord.TextChannel):
        with open('settings.json', 'r') as f:
            settings = json.load(f)
        await self.update_data_mod(settings, channel)
        with open('settings.json', 'w') as f:
            json.dump(settings, f)

