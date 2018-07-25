import discord
import discord.ext.commands as commands
from .utils import checks
import json


def setup(bot):
    bot.add_cog(Moderation(bot))


class Moderation:
    def __init__(self, bot):
        self.bot = bot

    async def on_guild_join(self, guild):
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)
            self.add_prefixes(prefixes, guild)
        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f)

    def add_prefixes(self, prefixes, guild: discord.Guild):
        if str(guild.id) not in prefixes:
            prefixes[str(guild.id)] = {}
            prefixes[str(guild.id)] = ["!!"]
        if str(guild.id) in prefixes:
            prefixes[str(guild.id)] = ["!!"]

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @checks.is_mod_enabled()
    async def purge(self, ctx, number: int, *, options: str = None):
        '''Purge a given amount of messages
        Add -m to not send the confirmation message'''
        if options == "-m":
            await ctx.message.channel.purge(limit=number)
        else:
            deleted = await ctx.message.channel.purge(limit=number)
            await ctx.send('Deleted {} message(s)'.format(len(deleted)))

    @commands.command()
    @commands.has_permissions(kick_members=True)
    @checks.is_mod_enabled()
    async def kick(self, ctx, member: discord.Member, *, reason: str = "None"):
        '''Used to kick given Member'''
        for i in {}:
            ctx.send({i})
        server = ctx.message.guild
        await server.kick(member, reason=reason)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @checks.is_mod_enabled()
    async def ban(self, ctx, member: discord.Member, *, reason: str = "None"):
        '''Used to ban given Member'''
        server = ctx.message.guild
        await server.ban(member, reason=reason)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @checks.is_mod_enabled()
    async def unban(self, ctx, member: discord.Member, *, reason: str = "None"):
        '''Used to unban given Member'''
        server = ctx.message.guild
        await server.unban(member, reason=reason)

    @commands.group(invoke_without_command=True, name="prefix")
    @checks.is_mod_enabled()
    async def pref(self, ctx):
        '''Info on the prefixes that can be used on this server
        [p]pref
        [p]pref add
        [p]pref remove
        '''
        try:
            prefixes_string = "\u200b"
            with open('prefixes.json', 'r') as f:
                prefixes = json.load(f)
            for x in prefixes[str(ctx.guild.id)]:
                if x != "":
                    prefixes_string += x + ", "
            prefixes_string.strip(", ")
            await ctx.send("```ini\n" \
            "What prefixes can i use?\n" \
            "[Default] You can always ping me to use my commands, example: @Itachi help\n" \
            "[Other]   You can set your own prefixes by using [p]prefix add or [p]prefix remove\n" \
            "          These are customizable per guild and default to [!!]\n" \
            "[Current] @Itachi, {1}```".format(self.bot.user.mention, prefixes_string))

        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            print('Failed to send prefix\n{}'.format(exc))

    @pref.command()
    @commands.has_permissions(administrator=True)
    async def add(self, ctx, *, prefix: str):
        '''Add a prefix for this server'''
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)
        if len(prefixes) >= 10:
            await ctx.send("The max amount of prefixes (10) has already been reached")
            await ctx.message.add_reaction('\N{CROSS MARK}')
        else:
            prefixes[str(ctx.guild.id)].append(prefix)
            await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')
        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f)


    @pref.command()
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx, *, prefix: str):
        '''Remove a prefix for this server'''
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)
        idx = prefixes[str(ctx.guild.id)].index(prefix)
        if idx is None:
            await ctx.send("There is no `{}` prefix".format(prefix))
            await ctx.message.add_reaction('\N{CROSS MARK}')
        else:
            prefixes[str(ctx.guild.id)].remove(prefix)
            await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')
        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f)

    @commands.command(name='cleanup')
    async def do_cleanup(self, ctx, limit: int = 20):
        """Cleanup a bot sessions messages.
        !Manage Messages is required to run this command fully!
        Parameters
        ------------
        limit: int [Optional]
            The max amount of messages to try and clean. This defaults to 20.
        Examples
        ----------
        <prefix>cleanup <limit>
            {ctx.prefix}cleanup 30
            {ctx.prefix}cleanup
        """
        messages = []

        async for message in ctx.channel.history(limit=limit):
            if message.content.startswith(ctx.prefix):
                messages.append(message)
            elif message.author == ctx.guild.me:
                messages.append(message)

        if not messages:
            return await ctx.send('No messages to delete...')
        await ctx.channel.delete_messages(messages)

        botm = len([m for m in messages if m.author == ctx.guild.me])
        userm = len(messages) - botm

        embed = discord.Embed(title='Cleanup',
                              description=f'Removed **{len(messages)}** messages successfully.',
                              colour=0xffd4d4)
        embed.set_footer(text=f'User Messages - {userm} | Bot Messages - {botm}')

        await ctx.send(embed=embed, delete_after=30)

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('`Latency: {0} ms`'.format(round(self.bot.latency*1000, 1)))


    @commands.command()
    @commands.is_owner()
    async def reload_all_prefixes(self, ctx):
        for guild in self.bot.guilds:
            with open('prefixes.json', 'r') as f:
                prefixes = json.load(f)
                self.add_prefixes(prefixes, guild)
            with open('prefixes.json', 'w') as f:
                json.dump(prefixes, f)
        await ctx.send("Done. All prefixes reset.")