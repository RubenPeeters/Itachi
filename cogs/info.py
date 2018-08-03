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
        try:
            embed = discord.Embed(description="Multipurpose Discord Bot\n"
                                              "__**General notice:**__\n"
                                              "Use [p]setu #(a text channel in your server) to receive major updates about the bot.\n"
                                              "Don't worry, I won't spam your server.\n"
                                              "Have a great time using Itachi!", color=0xA90000)
            embed.add_field(name="<:meowcrown:472052473364873216> Author", value="Ruben#9999", inline=False)
            embed.add_field(name="Donations", value="[Donations](https://paypal.me/Itachibot) are needed to keep the bot running. \n"
                                                                           "Any money you can spare is greatly appreciated, but don't feel obliged to donate.\n"
                                                    "\n")
            embed.add_field(name="Invite?",
                        value="[This is my invite link](https://discordapp.com/api/oauth2/authorize?client_id=457838617633488908&scope=bot&permissions=473052286)", inline=False)
            embed.add_field(name="Need help?",
                        value="[Join my server!](https://discord.gg/2XfmHUH)", inline=False)
            embed.set_footer(icon_url=self.bot.user.avatar_url, text="Replace [p] with the custom prefix in your server")
            await ctx.send(embed=embed)
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            print('Failed to send embed\n{}'.format(exc))

    @info.command()
    async def server(self, ctx):
        '''Show information on the current server'''
        try:
            server = ctx.message.guild
            roles = [x.name for x in server.role_hierarchy]
            role_length = len(roles)
            if role_length > 50:
                roles = roles[:50]
                roles.append('>>>> [50/%s] Roles' % len(roles))
            roles = ', '.join(roles);
            channelz = len(server.channels);
            join = discord.Embed(description='%s ' % (str(server)), title='Server Name', colour=0xA90000)
            join.set_thumbnail(url=server.icon_url);
            join.add_field(name='<:dblAdmin:471956486206128132> __Owner__', value=str(server.owner) + '\n' + str(server.owner.id))
            join.add_field(name='<:discord:471962154656858122> __ID__', value=str(server.id))
            join.add_field(name='<:users_icon:449826080682147840> __Member Count__', value=str(server.member_count))
            join.add_field(name='<:channels_icon:449825660064759809> __Text/Voice Channels__', value=str(channelz))
            join.add_field(name='<a:ablobsunglasses:468521148976463902> __Roles {}__'.format(str(role_length)), value=roles)
            await ctx.send(embed=join)
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
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


    @commands.command(name='perms', aliases=['perms_for', 'permissions'])
    @commands.guild_only()
    async def check_permissions(self, ctx, *, member: discord.Member=None):
        """A simple command which checks a members Guild Permissions.
        If member is not provided, the author will be checked."""

        if not member:
            member = ctx.author

        # Here we check if the value of each permission is True.
        perms = '\n'.join(perm for perm, value in member.guild_permissions if value)

        # And to make it look nice, we wrap it in an Embed.
        embed = discord.Embed(title='Permissions for:', description=ctx.guild.name, colour=member.colour)
        embed.set_author(icon_url=member.avatar_url, name=str(member))

        # \uFEFF is a Zero-Width Space, which basically allows us to have an empty field name.
        embed.add_field(name='\uFEFF', value=perms)

        await ctx.send(content=None, embed=embed)
        # Thanks to Gio for the Command.

    @commands.command(name='top_role', aliases=['toprole'])
    @commands.guild_only()
    async def show_toprole(self, ctx, *, member: discord.Member = None):
        """Simple command which shows the members Top Role."""

        if member is None:
            member = ctx.author

        await ctx.send(f'The top role for {member.display_name} is {member.top_role.name}')

    @commands.command()
    @commands.guild_only()
    async def joined(self, ctx, *, member: discord.Member):
        """Says when a member joined."""
        await ctx.send(f'{member.display_name} joined on {member.joined_at}')





