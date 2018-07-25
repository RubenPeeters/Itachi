import discord
from discord.ext import commands
from .utils import checks
import os
import json


def setup(bot):
    bot.add_cog(info(bot))


class info:
    def __init__(self, bot):
        self.bot = bot
        self.errorchannelid = 467672989232529418


    @commands.group(name="info", invoke_without_command=True)
    async def info(self, ctx):
        '''Show info on the bot, can also be used to send
        info on the server, a user or the configs
        [p]info server
        [p]info <user>
        [p]info config <cog/module>
        '''
        for x in self.bot.guilds:
            for chan in x.channels:
                if chan.id == self.errorchannelid:
                    errorchannel = chan
        try:
            embed = discord.Embed(title="Itachi", description="General Discord Bot", color=0xA90000)
            embed.add_field(name="Author", value="Ruben#9999",inline=False)
            embed.add_field(name="Server count", value=f"{len(self.bot.guilds)}",inline=False)
            embed.add_field(name="Invite",
                        value="[Invite link](https://discordapp.com/api/oauth2/authorize?client_id=457838617633488908&scope=bot&permissions=473052286)",inline=False)
            embed.add_field(name="Need help?",
                        value="[Server invite link](https://discord.gg/2XfmHUH)",inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            await errorchannel.send(
                'Failed to send info embed\n{}\n{}'.format(exc, ctx.guild.name))
            print('Failed to send embed\n{}'.format(exc))

    @info.command()
    async def server(self, ctx):
        '''Show information on the current server'''
        for x in self.bot.guilds:
            for chan in x.channels:
                if chan.id == self.errorchannelid:
                    errorchannel = chan
        try:
            server = ctx.message.guild
            roles = [x.name for x in server.role_hierarchy]
            role_length = len(roles)
            if role_length > 50:
                roles = roles[:50]
                roles.append('>>>> [50/%s] Roles' % len(roles))
            roles = ', '.join(roles);
            channelz = len(server.channels);
            time = str(server.created_at);
            time = time.split(' ');
            time = time[0];
            join = discord.Embed(description='%s ' % (str(server)), title='Server Name', colour=0xA90000)
            join.set_thumbnail(url=server.icon_url);
            join.add_field(name='__Owner__', value=str(server.owner) + '\n' + str(server.owner.id))
            join.add_field(name='__ID__', value=str(server.id))
            join.add_field(name='__Member Count__', value=str(server.member_count))
            join.add_field(name='__Text/Voice Channels__', value=str(channelz))
            join.add_field(name='__Roles {}__'.format(str(role_length)), value=roles)
            join.set_footer(text='Created: {}'.format(time))
            await ctx.send(embed=join)
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            await errorchannel.send(
                'Failed to send info server embed\n{}\n{}'.format(exc, ctx.guild.name))
            print('Failed to send embed\n{}'.format(exc))

    @info.command()
    async def user(self, ctx, user: discord.Member):
        '''Show information on user'''
        roles = ""
        for x in user.roles:
            roles = roles + x.name + ", "
        roles.strip(", ")
        embed = discord.Embed(title=f"Information on {user.name}", colour=0x7F81FF)
        embed.set_thumbnail(url=user.avatar_url)
        embed.add_field(name="Created at:", value=user.created_at, inline=False)
        embed.add_field(name="Joined at:", value=user.joined_at, inline=False)
        embed.add_field(name="Display name:", value=user.display_name, inline=False)
        embed.add_field(name="Roles:", value=roles, inline=False)
        embed.set_footer(text="Amaterasu!", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @info.command()
    async def config(self, ctx, cog: str = None):
        '''Show information about the config of cogs in this server'''
        os.chdir(r'/root/home/itachi')
        with open('guilds.json', 'r') as f:
            guilds = json.load(f)
        if cog is not None:
            await ctx.send("`{}: {}`".format(cog, guilds[str(ctx.guild.id)][cog]))
        else:
            to_send = ""
            for x in guilds[str(ctx.guild.id)]:
                to_send += "{}: {}".format("✅" if guilds[str(ctx.guild.id)][x] else "❌", x) + "\n"
            await ctx.send("```" + to_send + "```")

    @commands.command()
    async def avatar(self, ctx, *, member: discord.Member=None):
        embed = discord.Embed(color=0x7F81FF)
        if member is None:
            embed.set_image(url=ctx.author.avatar_url)
        else:
            embed.set_image(url=member.avatar_url)
        await ctx.send(embed=embed)





