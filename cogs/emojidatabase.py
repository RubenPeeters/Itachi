import discord
from discord.ext import commands
import requests
from .utils import checks
import copy
from .utils.paginator import EmotePaginator, CannotPaginate


def setup(bot):
    bot.add_cog(emojidatabase(bot))

class emojidatabase:

    def __init__(self, bot):
        self.bot = bot
        self.servers = [460816759554048000, 460816847437037580, 460816987912798252, 460817157756813312,
                        460817260341100556]
        self.errorchannelid = 467672989232529418


    async def on_command_error(self, ctx, error):
        embed = discord.Embed(title="Error", color=0xA90000)
        if isinstance(error, commands.NotOwner):
            embed.description = f"Sorry, but `{ctx.command.qualified_name}` can only be run by my owner."
            await ctx.send(embed=embed)
        if isinstance(error, commands.MissingPermissions):
            embed.description = f"Sorry, but you don't have sufficient permissions to run`{ctx.command.qualified_name}`"
            await ctx.send(embed=embed)

    async def on_message(self, message):
        if message.author.bot:
            return
        emotes = self.search_db(message.content)
        if emotes != "":
            await message.channel.send(emotes)

    def get_emote_strings(self, name: str):
        for guild_id in self.servers:
            server = self.bot.get_guild(guild_id)
            for emote in server.emojis:
                if emote.name.lower() == name.lower():
                    return str(emote)

    def search_db(self, message: str):
        emotes = ""
        if message.count("!") >= 2:
            for m in message.split("!"):
                for s in self.servers:
                    server = self.bot.get_guild(s)
                    for emo in server.emojis:
                        if m != "" or m is not None:
                            if m.lower() == emo.name.lower():
                                emotes += self.get_emote_strings(m)
        if emotes is not None or emotes != "":
            return emotes

    @commands.group(invoke_without_command=True, description="The base command for using the emote database")
    @checks.is_emojidatabase_enabled()
    async def emote(self, ctx):
        await ctx.send("Use !!emote `add`, `remove` or `search` to make use of this command")

    @emote.command()
    @checks.is_emojidatabase_enabled()
    async def add(self, ctx: commands.Context, *emojis: discord.PartialEmoji):
        '''Add an emote to the database'''
        duplicate = False
        await ctx.message.add_reaction('\N{HOURGLASS}')
        for emoji in emojis:
            for s in self.servers:
                for emo in self.bot.get_guild(s).emojis:
                    if emo.name.lower() == emoji.name.lower():
                        duplicate = True
                        await ctx.send("There already is an emote with that name.")
                        await ctx.message.remove_reaction('\N{HOURGLASS}', ctx.me)
                        await ctx.message.add_reaction('\N{CROSS MARK}')
                        break
            if not duplicate:
                if emoji.animated:
                    try:
                        if not duplicate:
                            for s in self.servers:
                                count = 0
                                for emo in self.bot.get_guild(s).emojis:
                                    if emo.animated:
                                        count += 1
                                if count < 50:
                                    usable_server_id = s
                                    break
                        server = self.bot.get_guild(usable_server_id)
                        response = requests.get(emoji.url)
                        await server.create_custom_emoji(name=emoji.name, image=response.content)
                        await ctx.message.remove_reaction('\N{HOURGLASS}', ctx.me)
                        await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')
                    except Exception as e:
                        exc = "{}: {}".format(type(e).__name__, e)
                        print('Failed to add animated emote\n{}'.format(exc))
                else:
                    try:
                        for s in self.servers:
                            count = 0
                            for emo in self.bot.get_guild(s).emojis:
                                if not emo.animated:
                                    count += 1
                            if count < 50:
                                usable_server_id = s
                                break
                        server = self.bot.get_guild(usable_server_id)
                        response = requests.get(emoji.url)
                        await server.create_custom_emoji(name=emoji.name, image=response.content)
                        await ctx.message.remove_reaction('\N{HOURGLASS}', ctx.me)
                        await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')
                    except Exception as e:
                        exc = "{}: {}".format(type(e).__name__, e)
                        print('Failed to add non-animated emote\n{}'.format(exc))

    @emote.command(aliases=['rem'])
    @checks.is_emojidatabase_enabled()
    async def remove(self, ctx: commands.Context, name: str):
        '''Remove an emote from the database'''
        try:
            await ctx.message.add_reaction('\N{HOURGLASS}')
            for s in self.servers:
                server = self.bot.get_guild(s)
                for emo in server.emojis:
                    if emo.name.lower() == name.lower():
                        await emo.delete()
                        await ctx.message.remove_reaction('\N{HOURGLASS}', ctx.me)
                        await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            print('Failed to remove emote\n{}'.format(exc))
            await ctx.message.remove_reaction('\N{HOURGLASS}', ctx.me)
            await ctx.message.add_reaction('\N{CROSS MARK}')

    @emote.command(aliases=['lf'])
    @checks.is_emojidatabase_enabled()
    async def search(self, ctx: commands.Context, name: str):
        '''Search for an emote in the database'''
        embed = discord.Embed(title=f"{name.upper()}")
        embed.set_author(name=ctx.message.author, icon_url=ctx.message.author.avatar_url)
        found = False
        try:
            await ctx.message.add_reaction('\N{HOURGLASS}')
            for s in self.servers:
                server = self.bot.get_guild(s)
                for emo in server.emojis:
                    if name.lower() in emo.name.lower():
                        embed.set_thumbnail(url=emo.url)
                        embed.add_field(name="\u200b", value=f"{emo}: `{emo.name}`")
                        found = True
            if not found:
                embed.add_field(name="\u200b", value=f"No emote that contains `{name}` found")
                await ctx.message.remove_reaction('\N{HOURGLASS}', ctx.me)
                await ctx.message.add_reaction('\N{CROSS MARK}')
            else:
                await ctx.message.remove_reaction('\N{HOURGLASS}', ctx.me)
                await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')
            await ctx.send(embed=embed)
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            print('Failed to find emote\n{}'.format(exc))
            await ctx.message.remove_reaction('\N{HOURGLASS}', ctx.me)
            await ctx.message.add_reaction('\N{CROSS MARK}')

    @emote.command()
    @checks.is_emojidatabase_enabled()
    async def info(self, ctx):
        emote_start = "<"
        emote_end = ">"
        emote_points = ":"
        emotelist = []
        try:
            for s in self.servers:
                for emo in self.bot.get_guild(s).emojis:
                    infostring = ""
                    if emo.animated:
                        # <a:name:id>
                        emote = emote_start + "a" + emote_points + str(emo.name) + emote_points + str(emo.id) + emote_end
                    else:
                        # <:name:id>
                        emote = emote_start + emote_points + str(emo.name) + emote_points + str(emo.id) + emote_end
                    infostring += emote + " : " + emo.name + "\n"
                    emotelist.append(infostring.lower())
            emotelist.sort()
            p = EmotePaginator(ctx, emotelist)
            await p.paginate()
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            print('Failed to show emoji database\n{}'.format(exc))

    @commands.command(aliases=["edb"])
    @checks.is_emojidatabase_enabled()
    async def emotedb(self, ctx, *, name: str):
        emotes = ""
        found = False
        for guild_id in self.servers:
            server = self.bot.get_guild(guild_id)
            for emote in server.emojis:
                if emote.name.lower() in name.lower():
                    emotes += "   " + str(emote)
                    found = True
        await ctx.send(emotes)
        if found == False:
            await ctx.send(f"There is no emote named '{name}' in the database.")


