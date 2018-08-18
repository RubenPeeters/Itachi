import asyncio
import discord

class CannotPaginate(Exception):
    pass

class Pages:
    """Implements a paginator that queries the user for the
    pagination interface.
    Pages are 1-index based, not 0-index based.
    If the user does not reply within 2 minutes, the pagination
    interface exits automatically.
    """
    def __init__(self, ctx, *, entries, per_page=10):
        self.bot = ctx.bot
        self.entries = entries
        self.message = ctx.message
        self.channel = ctx.channel
        self.author = ctx.message.author
        self.message_text = ""
        self.title = ""
        self.per_page = per_page
        pages, left_over = divmod(len(self.entries), self.per_page)
        if left_over:
            pages += 1
        self.maximum_pages = pages
        self.text_start = "```\n"
        self.text_end = "```"
        self.description = ""
        self.footer = ""
        self.paginating = len(entries) > per_page
        self.reaction_emojis = [
            ('\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}', self.first_page),
            ('\N{BLACK LEFT-POINTING TRIANGLE}', self.previous_page),
            ('\N{BLACK RIGHT-POINTING TRIANGLE}', self.next_page),
            ('\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}', self.last_page),
            ('\N{INPUT SYMBOL FOR NUMBERS}', self.numbered_page ),
            ('\N{BLACK SQUARE FOR STOP}', self.stop_pages),
            ('\N{INFORMATION SOURCE}', self.show_help),
        ]

        if ctx.guild is not None:
            self.permissions = self.message.channel.permissions_for(ctx.guild.me)
        else:
            self.permissions = self.message.channel.permissions_for(ctx.bot.user)


    def get_page(self, page):
        base = (page - 1) * self.per_page
        return self.entries[base:base + self.per_page]

    async def show_page(self, page, *, first=False):
        self.current_page = page
        entries = self.get_page(page)
        p = []
        for t in enumerate(entries, 1 + ((page - 1) * self.per_page)):
            p.append('%s. %s' % t)

        self.footer = 'Page %s/%s (%s entries)' % (page, self.maximum_pages, len(self.entries))

        if not self.paginating:
            self.description = '\n'.join(p)
            self.message_text = f"{self.text_start}{self.title}\n{self.description}\n\n{self.body}\n\n{self.footer}\n{self.text_end}"
            return await self.message.channel.send(self.message)

        if not first:
            self.description = '\n'.join(p)
            self.message_text = f"{self.text_start}{self.title}\n{self.description}\n\n{self.body}\n\n{self.footer}\n{self.text_end}"
            await self.message.edit(content=self.message_text)
            return

        # verify we can actually use the pagination session
        if not self.permissions.add_reactions:
            raise CannotPaginate('Bot does not have add reactions permission.')

        if not self.permissions.read_message_history:
            raise CannotPaginate('Bot does not have Read Message History permission.')

        p.append('')
        p.append('Confused? React with \N{INFORMATION SOURCE} for more info.')
        self.description = '\n'.join(p)
        self.message_text = f"{self.text_start}{self.title}\n{self.description}\n\n{self.body}\n\n{self.footer}\n{self.text_end}"
        self.message = await self.message.channel.send(self.message_text)
        for (reaction, _) in self.reaction_emojis:
            if self.maximum_pages == 2 and reaction in ('\u23ed', '\u23ee'):
                # no |<< or >>| buttons if we only have two pages
                # we can't forbid it if someone ends up using it but remove
                # it from the default set
                continue
            try:
                await self.message.add_reaction(reaction)
            except discord.NotFound:
                # If the message isn't found, we don't care about clearing anything
                return

    async def checked_show_page(self, page):
        if page != 0 and page <= self.maximum_pages:
            await self.show_page(page)

    async def first_page(self):
        """goes to the first page"""
        await self.show_page(1)

    async def last_page(self):
        """goes to the last page"""
        await self.show_page(self.maximum_pages)

    async def next_page(self):
        """goes to the next page"""
        await self.checked_show_page(self.current_page + 1)

    async def previous_page(self):
        """goes to the previous page"""
        await self.checked_show_page(self.current_page - 1)

    async def show_current_page(self):
        if self.paginating:
            await self.show_page(self.current_page)

    async def numbered_page(self):
        """lets you type a page number to go to"""
        to_delete = []
        to_delete.append(await self.message.channel.send('What page do you want to go to?'))

        def message_check(m):
            return m.author == self.author and \
                   self.channel == m.channel and \
                   m.content.isdigit()

        try:
            msg = await self.bot.wait_for('message', check=message_check, timeout=30.0)
        except asyncio.TimeoutError:
            to_delete.append(await self.message.channel.send('Took too long.'))
            await asyncio.sleep(5)
        else:
            page = int(msg.content)
            to_delete.append(msg)
            if page != 0 and page <= self.maximum_pages:
                await self.show_page(page)
            else:
                to_delete.append(await self.message.channel.send(f'Invalid page given. ({page}/{self.maximum_pages})'))
                await asyncio.sleep(5)

        try:
            await self.message.channel.delete_messages(to_delete)
        except Exception:
            pass

    async def show_help(self):
        """shows this message"""
        messages = ['Welcome to the interactive paginator!\n']
        messages.append('This interactively allows you to see pages of text by navigating with ' \
                        'reactions. They are as follows:\n')

        for (emoji, func) in self.reaction_emojis:
            messages.append('%s %s' % (emoji, func.__doc__))

        self.description = '\n'.join(messages)
        self.footer = 'We were on page %s before this message.' % self.current_page
        self.message_text = f"{self.text_start}{self.title}\n{self.description}\n\n{self.body}\n\n{self.footer}\n{self.text_end}"
        self.message.edit(content=self.message_text)

        async def go_back_to_current_page():
            await asyncio.sleep(60.0)
            await self.show_current_page()

        self.bot.loop.create_task(go_back_to_current_page())

    async def stop_pages(self):
        """stops the interactive pagination session"""
        await self.message.delete()
        self.paginating = False

    def react_check(self, reaction, user):
        if user is None or user.id != self.author.id:
            return False

        for (emoji, func) in self.reaction_emojis:
            if reaction.emoji == emoji:
                self.match = func
                return True
        return False

    async def paginate(self):
        """Actually paginate the entries and run the interactive loop if necessary."""
        first_page = self.show_page(1, first=True)
        if not self.paginating:
            await first_page
        else:
            # allow us to react to reactions right away if we're paginating
            self.bot.loop.create_task(first_page)

        while self.paginating:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=self.react_check, timeout=120.0)
            except asyncio.TimeoutError:
                self.paginating = False
                try:
                    await self.message.clear_reactions()
                except:
                    pass
                finally:
                    break

            try:
                await self.message.remove_reaction(reaction, user)
            except:
                pass # can't remove it so don't bother doing so

            await self.match()

import itertools
import inspect
import re

# ?help
# ?help Cog
# ?help command
#   -> could be a subcommand

_mention = re.compile(r'<@\!?([0-9]{1,19})>')

def cleanup_prefix(bot, prefix):
    m = _mention.match(prefix)
    if m:
        user = bot.get_user(int(m.group(1)))
        if user:
            return f'@{user.name} '
    return prefix

async def _can_run(cmd, ctx):
    try:
        return await cmd.can_run(ctx)
    except:
        return False

def _command_signature(cmd):
    # this is modified from discord.py source
    # which I wrote myself lmao

    result = [cmd.qualified_name]
    if cmd.usage:
        result.append(cmd.usage)
        return ' '.join(result)

    params = cmd.clean_params
    if not params:
        return ' '.join(result)

    for name, param in params.items():
        if param.default is not param.empty:
            # We don't want None or '' to trigger the [name=value] case and instead it should
            # do [name] since [name=None] or [name=] are not exactly useful for the user.
            should_print = param.default if isinstance(param.default, str) else param.default is not None
            if should_print:
                result.append(f'[{name}={param.default!r}]')
            else:
                result.append(f'[{name}]')
        elif param.kind == param.VAR_POSITIONAL:
            result.append(f'[{name}...]')
        else:
            result.append(f'<{name}>')

    return ' '.join(result)


class HelpPaginator(Pages):
    def __init__(self, ctx, entries, *, per_page=4):
        super().__init__(ctx, entries=entries, per_page=per_page)
        self.total = len(entries)

    @classmethod
    async def from_cog(cls, ctx, cog):
        cog_name = cog.__class__.__name__

        # get the commands
        entries = sorted(ctx.bot.get_cog_commands(cog_name), key=lambda c: c.name)


        # remove the ones we can't run
        entries = [cmd for cmd in entries if (await _can_run(cmd, ctx)) and not cmd.hidden]
        for cmd in entries:
            print(cmd)
        self = cls(ctx, entries)
        self.title = f'{cog_name} commands: '
        self.description = inspect.getdoc(cog)
        self.prefix = cleanup_prefix(ctx.bot, ctx.prefix)


        return self

    @classmethod
    async def from_command(cls, ctx, command):
        try:
            entries = sorted(command.commands, key=lambda c: c.name)
        except AttributeError:
            entries = []
        else:
            entries = [cmd for cmd in entries if (await _can_run(cmd, ctx)) and not cmd.hidden]

        self = cls(ctx, entries)
        self.title = command.signature

        if command.description:
            self.description = f'{command.description}\n\n{command.help}'
        else:
            self.description = command.help or 'No help given.'

        self.prefix = cleanup_prefix(ctx.bot, ctx.prefix)
        return self

    @classmethod
    async def from_bot(cls, ctx):
        def key(c):
            return c.cog_name or '\u200bMisc'

        entries = sorted(ctx.bot.commands, key=key)
        nested_pages = []
        per_page = 9

        # 0: (cog, desc, commands) (max len == 9)
        # 1: (cog, desc, commands) (max len == 9)
        # ...

        for cog, commands in itertools.groupby(entries, key=key):
            plausible = [cmd for cmd in commands if (await _can_run(cmd, ctx)) and not cmd.hidden]
            if len(plausible) == 0:
                continue
            description = ctx.bot.get_cog(cog)
            if description is None:
                description = ""
            else:
                description = inspect.getdoc(description) or ""

            nested_pages.extend((cog, description, plausible[i:i + per_page]) for i in range(0, len(plausible), per_page))

        self = cls(ctx, nested_pages, per_page=1) # this forces the pagination session
        self.prefix = cleanup_prefix(ctx.bot, ctx.prefix)

        # swap the get_page implementation with one that supports our style of pagination
        self.get_page = self.get_bot_page
        self._is_bot = True

        # replace the actual total
        self.total = sum(len(o) for _, _, o in nested_pages)
        return self

    def get_bot_page(self, page):
        cog, description, commands = self.entries[page - 1]
        self.title = f'{cog.title()} Commands'
        self.description = description
        return commands

    async def show_page(self, page, *, first=False):
        self.current_page = page
        entries = self.get_page(page)

        self.body = ""

        self.footer = f'Use {self.prefix}help (insert command here) for more info on a command. Support server: https:\u200b//discord.gg/2XfmHUH'
        signature = _command_signature

        for entry in entries:
            self.body += f"⛶ {signature(entry)}\n{entry.short_doc or 'No help given'}\n\n"

        if self.maximum_pages:
            self.title += f' Page {page}/{self.maximum_pages} ({self.total})'

        if not self.paginating:
            self.message_text = f"{self.text_start}{self.title}\n{self.description}\n\n{self.body}\n\n{self.footer}\n{self.text_end}"
            return await self.message.channel.send(self.message_text)

        if not first:
            self.message_text = f"{self.text_start}{self.title}\n{self.description}\n\n{self.body}\n\n{self.footer}\n{self.text_end}"
            await self.message.edit(content=self.message_text)
            return
        self.message_text = f"{self.text_start}{self.title}\n{self.description}\n\n{self.body}\n\n{self.footer}\n{self.text_end}"
        self.message = await self.message.channel.send(self.message_text)
        for (reaction, _) in self.reaction_emojis:
            if self.maximum_pages == 2 and reaction in ('\u23ed', '\u23ee'):
                # no |<< or >>| buttons if we only have two pages
                # we can't forbid it if someone ends up using it but remove
                # it from the default set
                continue

            await self.message.add_reaction(reaction)

    async def show_help(self):
        """shows this message"""

        self.title = 'Paginator help'
        self.description = 'Hello! Welcome to the help page.'

        messages = [f'{emoji} {func.__doc__}' for emoji, func in self.reaction_emojis]
        text = '\n'.join(messages)
        self.body = f'What are these reactions for?\n{text}'
        self.footer = f'We were on page {self.current_page} before this message.'
        self.message_text = f"{self.text_start}{self.title}\n{self.description}\n\n{self.body}\n\n{self.footer}\n{self.text_end}"
        await self.message.edit(content=self.message_text)

        async def go_back_to_current_page():
            await asyncio.sleep(30.0)
            await self.show_current_page()

        self.bot.loop.create_task(go_back_to_current_page())
