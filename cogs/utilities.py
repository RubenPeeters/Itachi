import discord
import discord.ext.commands as commands
import random
from .utils import checks


def setup(bot):
    bot.add_cog(utils(bot))

class utils:
    def __init__(self, bot):
        self.bot = bot
        self.errorchannelid = 467672989232529418


    @commands.command()
    async def quote(self, ctx, messageid: int):
        '''Quote a certain message using its ID'''
        for x in self.bot.guilds:
            for chan in x.channels:
                if chan.id == self.errorchannelid:
                    self.errorchannel = chan
        for channel in ctx.guild.channels:
            try:
                msg = await channel.get_message(messageid)
            except:
                continue
        try:
            embed = discord.Embed(description=f"{msg.content}", color=0xA90000)
            embed.set_author(name=msg.author, icon_url=msg.author.avatar_url)
            embed.add_field(name="Sent at:", value=str(msg.created_at))
            await ctx.send(embed=embed)
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            await self.errorchannel.send(
                'Failed to create tag\n{}\n{}'.format(exc, ctx.guild.name))
            await ctx.send(f"This type of message is not yet supported, sorry {ctx.message.author.mention}")
        try:
            await ctx.message.delete()
        except:
            await ctx.message.add_reaction('\N{CROSS MARK}')

    @commands.command(aliases=['color', 'colour'])
    async def _color(self, ctx, *, color: hex):
        for x in self.bot.guilds:
            for chan in x.channels:
                if chan.id == self.errorchannelid:
                    self.errorchannel = chan
        try:
            embed = discord.Embed(title=str(color), color=color)
            await ctx.send(embed=embed)
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            await self.errorchannel.send(
                'Failed to send color\n{}\n{}'.format(exc, ctx.guild.name))
            print('Failed to send color\n{}'.format(exc))



