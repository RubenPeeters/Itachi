import discord
import discord.ext.commands as commands
import datetime
from collections import Counter


def setup(bot):
    bot.add_cog(stats(bot))
    if not hasattr(bot, 'command_stats'):
        bot.command_stats = Counter()

    if not hasattr(bot, 'socket_stats'):
        bot.socket_stats = Counter()


class stats:
    def __init__(self, bot):
        self.bot = bot

    def get_bot_uptime(self, *, brief=False):
        now = datetime.datetime.utcnow()
        delta = now - self.bot.uptime
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        if not brief:
            if days:
                fmt = '{d} days, {h} hours, {m} minutes, and {s} seconds'
            else:
                fmt = '{h} hours, {m} minutes, and {s} seconds'
        else:
            fmt = '{h}h {m}m {s}s'
            if days:
                fmt = '{d}d ' + fmt

        return fmt.format(d=days, h=hours, m=minutes, s=seconds)

    @commands.command()
    async def uptime(self, ctx):
        """Tells you how long the bot has been up for."""
        try:
            embed = discord.Embed(color=0xA90000)
            embed.set_thumbnail(url="https://i.ytimg.com/vi/e5HfCcII84M/maxresdefault.jpg")
            embed.add_field(name="Uptime", value=self.get_bot_uptime())
            await ctx.send(embed=embed)
        except Exception as e:
            print(e)

    @commands.command()
    async def stats(self, ctx):
        """Tells you information about the bot itself."""
        try:
            embed = discord.Embed(title='Statistics for Itachi', color=0xA90000 )
            owner = self.bot.get_user(self.bot.owner_id)
            embed.set_author(name=str(owner), icon_url=owner.avatar_url)

            # statistics
            total_members = sum(1 for _ in self.bot.get_all_members())
            total_online = len({m.id for m in self.bot.get_all_members() if m.status is not discord.Status.offline})
            total_unique = len(self.bot.users)

            voice_channels = []
            text_channels = []
            for guild in self.bot.guilds:
                voice_channels.extend(guild.voice_channels)
                text_channels.extend(guild.text_channels)

            text = len(text_channels)
            voice = len(voice_channels)

            embed.add_field(name='<:users_icon:449826080682147840> Members', value='• Total: {}\n• Unique: {}\n'
                                                                                   '• Unique online: {} '
                            .format(total_members, total_unique, total_online))
            embed.add_field(name='<:channels_icon:449825660064759809> Channels', value='• Total: {}\n• Text: {}'
                                                                                       '\n• Voice: {}'
                            .format(text + voice, text, voice))
            embed.add_field(name='<:guilds_icon:449825671561216011> Guilds', value="• Total: " +
                                                                                   str(len(self.bot.guilds)))
            embed.add_field(name=':clock: Uptime', value=self.get_bot_uptime(brief=True))
            embed.set_footer(text='Made with rewrite branch discord.py', icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send('{}: {}'.format(type(e).__name__, e))

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('`Latency: {0} ms`'.format(round(self.bot.latency * 1000, 1)))


