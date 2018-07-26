import discord
import discord.ext.commands as commands
import inspect
import requests
import io
from .utils import checks
from contextlib import redirect_stdout
import textwrap
import traceback
import datetime
import copy
import json


def setup(bot):
    bot.add_cog(owner(bot))

startup_extensions = ["cogs.mod", "cogs.owner", "cogs.misc", "cogs.lookup", "cogs.tags", "cogs.emoji", "cogs.coins", "cogs.emojidatabase", "cogs.config", "cogs.info", "cogs.stats", "cogs.fun", "cogs.settings"]

class owner:
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.sessions = set()
        self.errorchannelid = 467672989232529418

    async def __error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.send('This command can not be used in DMs.')
            except discord.HTTPException:
                pass

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'`{error.param.name}` is a required argument which is missing.')

    def cleanup_code(self, content):
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])
        return content.strip('` \n')

    def get_syntax_error(self, e):
        if e.text is None:
            return f'```py\n{e.__class__.__name__}: {e}\n```'
        return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'

    async def __local_check(self, ctx):
        if not await self.bot.is_owner(ctx.author):
            raise commands.NotOwner()
        return True

    @commands.command(name='source', aliases=['sauce'], hidden=True)
    @checks.is_owner_enabled()
    async def source(self, ctx: commands.Context, *, command):
        """Displays the source code of a command."""
        cmd = self.bot.get_command(command)
        if not cmd:
            return await ctx.send(f"I don't have a command with name `{command}`.")

        lines = []
        for line in inspect.getsourcelines(cmd.callback)[0]:
            line = line.rstrip().replace('`​`​`', '`\u200b`\u200b`')
            if line.startswith('    '):
                line = line[4:]
            lines.append(line)
        output = '\n'.join(lines)
        await ctx.send(f"```py\n{output}```")

    @commands.command(hidden=True)
    @checks.is_owner_enabled()
    async def load(self, ctx, *, module: str):
        """Loads a module."""
        await ctx.message.add_reaction('\N{HOURGLASS}')
        try:
            self.bot.load_extension(module)
        except Exception as e:
            await ctx.message.remove_reaction('\N{HOURGLASS}', ctx.me)
            await ctx.message.add_reaction('\N{CROSS MARK}')
            await ctx.send('{}: {}'.format(type(e).__name__, e))
        else:
            await ctx.message.remove_reaction('\N{HOURGLASS}', ctx.me)
            await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')

    @commands.command(hidden=True)
    @checks.is_owner_enabled()
    async def unload(self, ctx, *, module: str):
        """Unloads a module."""
        await ctx.message.add_reaction('\N{HOURGLASS}')
        try:
            self.bot.unload_extension(module)
        except Exception as e:
            await ctx.message.remove_reaction('\N{HOURGLASS}', ctx.me)
            await ctx.message.add_reaction('\N{CROSS MARK}')
            await ctx.send('{}: {}'.format(type(e).__name__, e))
        else:
            await ctx.message.remove_reaction('\N{HOURGLASS}', ctx.me)
            await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')

    @commands.command(name='reload', hidden=True)
    @checks.is_owner_enabled()
    async def _reload(self, ctx, *, module: str=None):
        """Reloads a module or if no cog is specified, reloads all."""
        if module is None or module == "all":
            await ctx.message.add_reaction('\N{HOURGLASS}')
            try:
                for extension in startup_extensions:
                    self.bot.unload_extension(extension)
                    self.bot.load_extension(extension)
            except Exception as e:
                await ctx.message.remove_reaction('\N{HOURGLASS}', ctx.me)
                await ctx.message.add_reaction('\N{CROSS MARK}')
                await ctx.send('{}: {}'.format(type(e).__name__, e))
            else:
                await ctx.message.remove_reaction('\N{HOURGLASS}', ctx.me)
                await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')
        else:
            await ctx.message.add_reaction('\N{HOURGLASS}')
            try:
                self.bot.unload_extension(module)
                self.bot.load_extension(module)
            except Exception as e:
                await ctx.message.remove_reaction('\N{HOURGLASS}', ctx.me)
                await ctx.message.add_reaction('\N{CROSS MARK}')
                await ctx.send('{}: {}'.format(type(e).__name__, e))
            else:
                await ctx.message.remove_reaction('\N{HOURGLASS}', ctx.me)
                await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')

    @commands.command(hidden=True)
    async def setavatar(self, ctx, *, url: str):
        try:
            response = requests.get(url)
            await self.bot.user.edit(avatar=response.content)
        except Exception as e:
            await ctx.send('{}: {}'.format(type(e).__name__, e))

    @commands.command(aliases=["setum"], hidden=True)
    async def setusername(self, ctx, *, name: str):
        try:
            await self.bot.user.edit(username=name)
        except Exception as e:
            await ctx.send('{}: {}'.format(type(e).__name__, e))

    @commands.command(name="upd")
    async def _update(self, ctx, *, update: str):
        with open('settings.json', 'r') as f:
            settings = json.load(f)
        for x in settings:
            channel_id = x["update"]
            print(channel_id)
            guild = discord.utils.get(self.bot.guilds, id=int(x))
            channel = discord.utils.get(guild.channels, id=channel_id)
            print(channel)
            await channel.send(update)

    @commands.command(pass_context=True, hidden=True, name='eval')
    async def _eval(self, ctx, *, body: str):
        """Evaluates a code"""

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')

    @commands.command(name='say', hidden=True)
    @checks.is_owner_enabled()
    async def _echo(self, ctx, *, text: str):
        await ctx.message.delete()
        await ctx.send(text)

    @commands.command(name='sudo', hidden=True)
    async def sudo(self, ctx: commands.Context, target: discord.Member, *, command: str):
        """Thanks to Christina"""
        fake_msg = copy.copy(ctx.message)
        fake_msg.content = ctx.prefix + command
        fake_msg.author = target
        new_ctx = await self.bot.get_context(fake_msg)
        await self.bot.invoke(new_ctx)




