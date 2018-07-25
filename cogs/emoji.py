import discord
import requests
import io
import re
from discord.ext import commands
from .utils import checks

'''Tools relating to custom emoji manipulation and viewing.'''
def setup(bot):
    bot.add_cog(Emoji(bot))

class Emoji:

    def __init__(self, bot):
        self.bot = bot
        self.servers = [460816759554048000, 460816847437037580, 460816987912798252, 460817157756813312,
                        460817260341100556]
        self.errorchannelid = 467672989232529418

    def find_emoji(self, msg):
        # Looking for emojis with regex
        msg = re.sub("<a?:(.+):([0-9]+)>", "\\2", msg)

        name = None

        # Look for the found emoji in guilds that the bot is in
        for guild in self.bot.guilds:
            for emoji in guild.emojis:
                if msg.strip().lower() in emoji.name.lower():
                    name = emoji.name + (".gif" if emoji.animated else ".png")
                    url = emoji.url
                    id = emoji.id
                    guild_name = guild.name
                if msg.strip() in (str(emoji.id), emoji.name):
                    name = emoji.name + (".gif" if emoji.animated else ".png")
                    url = emoji.url
                    return name, url, emoji.id, guild.name
        if name:
            return name, url, id, guild_name

    @commands.group(invoke_without_command=True)
    @checks.is_emoji_enabled()
    async def emoji(self, ctx, *, msg):
        """
        View, copy, add or remove emoji.
        Usage:
        1) [p]emoji <emoji> - View a large image of a given emoji. Use [p]emoji s for additional info.
        2) [p]emoji copy <emoji> - Copy a custom emoji on another server and add it to the current server if you have the permissions.
        3) [p]emoji add <url> - Add a new emoji to the current server if you have the permissions.
        4) [p]emoji remove <emoji> - Remove an emoji from the current server if you have the permissions
        """
        await ctx.message.delete()
        emojis = msg.split()
        if msg.startswith('s '):
            emojis = emojis[1:]
            get_guild = True
        else:
            get_guild = False

        if len(emojis) > 5:
            return await ctx.send("Maximum of 5 emojis at a time.")

        images = []
        for emoji in emojis:
            name, url, id, guild = self.find_emoji(emoji)
            if url == "":
                await ctx.send("Could not find {}. Skipping.".format(emoji))
                continue
            response = requests.get(url, stream=True)
            if response.status_code == 404:
                await ctx.send(
                    "Emoji {} not available. Open an issue on <https://github.com/astronautlevel2/twemoji> with the name of the missing emoji".format(
                        emoji))
                continue

            img = io.BytesIO()
            for block in response.iter_content(1024):
                if not block:
                    break
                img.write(block)
            img.seek(0)
            images.append((guild, str(id), url, discord.File(img, name)))

        for (guild, id, url, file) in images:
            if ctx.channel.permissions_for(ctx.author).attach_files:
                if get_guild:
                    await ctx.send(content='**ID:** {}\n**Server:** {}'.format(id, guild), file=file)
                else:
                    await ctx.send(file=file)
            else:
                if get_guild:
                    await ctx.send('**ID:** {}\n**Server:** {}\n**URL: {}**'.format(id, guild, url))
                else:
                    await ctx.send(url)
            file.close()

    @emoji.command(pass_context=True, aliases=["steal"])
    @commands.has_permissions(manage_emojis=True)
    @checks.is_emoji_enabled()
    async def copy(self, ctx, *, msg):
        '''Copy an emote from another server the bot is in'''
        await ctx.message.delete()
        msg = re.sub("<:(.+):([0-9]+)>", "\\2", msg)

        match = None
        exact_match = False
        for guild in self.bot.guilds:
            for emoji in guild.emojis:
                if msg.strip().lower() in str(emoji):
                    match = emoji
                if msg.strip() in (str(emoji.id), emoji.name):
                    match = emoji
                    exact_match = True
                    break
            if exact_match:
                break

        if not match:
            return await ctx.send(self.bot.bot_prefix + 'Could not find emoji.')

        response = requests.get(match.url)
        emoji = await ctx.guild.create_custom_emoji(name=match.name, image=response.content)
        await ctx.send(
            "Successfully added the emoji {0.name} <{1}:{0.name}:{0.id}>!".format(emoji,
                                                                                                        "a" if emoji.animated else ""))

    @emoji.command(pass_context=True)
    @commands.has_permissions(manage_emojis=True)
    @checks.is_emoji_enabled()
    async def add(self, ctx, name, url):
        '''Manuall add an emoji to the current server'''
        await ctx.message.delete()
        try:
            response = requests.get(url)
        except (requests.exceptions.MissingSchema, requests.exceptions.InvalidURL, requests.exceptions.InvalidSchema,
                requests.exceptions.ConnectionError):
            return await ctx.send( "The URL you have provided is invalid.")
        if response.status_code == 404:
            return await ctx.send("The URL you have provided leads to a 404.")
        try:
            emoji = await ctx.guild.create_custom_emoji(name=name, image=response.content)
        except discord.InvalidArgument:
            return await ctx.send("Invalid image type. Only PNG, JPEG and GIF are supported.")
        await ctx.send(
            "Successfully added the emoji {0.name} <{1}:{0.name}:{0.id}>!".format(emoji,
                                                                                                        "a" if emoji.animated else ""))

    @emoji.command(pass_context=True)
    @commands.has_permissions(manage_emojis=True)
    @checks.is_emoji_enabled()
    async def remove(self, ctx, name):
        '''Remove an emote from the server'''
        await ctx.message.delete()
        emotes = [x for x in ctx.guild.emojis if x.name == name]
        emote_length = len(emotes)
        if not emotes:
            return await ctx.send("No emotes with that name could be found on this server.")
        for emote in emotes:
            await emote.delete()
        if emote_length == 1:
            await ctx.send( "Successfully removed the {} emoji!".format(name))
        else:
            await ctx.send(
                "Successfully removed {} emoji with the name {}.".format(emote_length, name))


