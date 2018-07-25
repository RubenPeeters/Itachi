import discord
from discord.ext import commands
import json
import os
import asyncio
from itertools import cycle
import configparser
import datetime
import traceback

config = configparser.ConfigParser()
config.read("config.ini")
if os.getenv("TOKEN"):
    TOKEN = os.getenv("TOKEN")
else:
    TOKEN = config["DEFAULT"]["token"]

startup_extensions = ["cogs.mod",
                      "cogs.owner",
                      "cogs.misc",
                      "cogs.lookup",
                      "cogs.tags",
                      #"cogs.emoji",
                      #"cogs.coins",
                      "cogs.emojidatabase",
                      "cogs.config",
                      "cogs.info",
                      "cogs.utilities",
                      "cogs.fun",
                      "cogs.stats",
                      "cogs.chess",
                      "cogs.images",
                      "cogs.steam"]
status = ["Use !!help to find out what i can do!",
          "Need help? Join my server (!!info)",
          "with your head"]


def _prefix_callable(bot, msg):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
    user_id = bot.user.id
    base = ['<@{}> '.format(user_id)]
    if msg.guild is None:
        base.append('!!')
        base.append('')
    else:
        base.extend(prefixes[str(msg.guild.id)])
    return base


class Itachi(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix=_prefix_callable)
        self.owner_server_id = 457833113771442201
        self.owner_id = 150907968068648960
        self.logging_id = 468459817015705621
        self.join_id = 470523938124988437
        for extension in startup_extensions:
            try:
                self.load_extension(extension)
            except Exception as e:
                print('Failed to load extension {}.'.format(extension))

    async def get_logchannel(self):
        for x in self.guilds:
            if x.id == self.owner_server_id:
                log_channel = discord.utils.get(x.channels, id=self.logging_id)
        return log_channel

    async def get_log_joining_channel(self):
        for x in self.guilds:
            if x.id == self.owner_server_id:
                log_joining_channel = discord.utils.get(x.channels, id=self.join_id)
        return log_joining_channel

    async def get_invoke_error_channel(self):
        for x in self.guilds:
            if x.id == self.owner_server_id:
                channel = discord.utils.get(x.channels, id=self.invoke_error)
        return channel

    async def on_ready(self):
        print('Logged in as')
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()
        print(self.user.name)
        print(self.user.id)
        print('------')
        self.loop.create_task(self.change_status())

    async def on_command_completion(self, ctx):
        logchannel = await self.get_logchannel()
        if ctx.guild is not None:
            await logchannel.send("```"
                                  "✅ Command succesful\n"
                                  "Guild: {} ID: {}\n"
                                  "Member: {}\n"
                                  "Command: {}```".format(ctx.guild, ctx.guild.id, ctx.author, ctx.command.name))
        else:
            await logchannel.send("```"
                                  "✅ Command succesful\n"
                                  "Private Message\n"
                                  "Member: {}\n"
                                  "Command: {}```".format(ctx.author, ctx.command.name))

    async def on_command_error(self, ctx, exception):
        logchannel = await self.get_logchannel()
        exception = getattr(exception, 'original', exception)
        tb = ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__, chain=False))
        if ctx.guild is not None:
            if isinstance(exception, commands.CommandInvokeError):
                await logchannel.send("```py\n"
                                      "❌ Command failed\n"
                                      "Guild: {} ID: {}\n"
                                      "Member: {}\n"
                                      "Error: {}: {}\n"
                                      "Traceback: ()```".format(ctx.guild, ctx.guild.id, ctx.author, type(exception).__name__, exception, tb))

        else:
            if isinstance(exception, commands.CommandInvokeError):
                await logchannel.send("```py\n"
                                      "❌ Command failed\n"
                                      "Private Message\n"
                                      "Member: {}\n"
                                      "Error: {}: {}\n"
                                      "Traceback: {}```".format(ctx.author, type(exception).__name__, exception, tb))


    async def on_guild_join(self, guild):
        logchannel = await self.get_log_joining_channel()
        with open('guilds.json', 'r') as f:
            guilds = json.load(f)
            await self.add_guild_permissions(guilds, guild)
            embed = discord.Embed(title="Hi! I'm Itachi", color=0xA90000)
            embed.add_field(name="Introduction <:blobwave:464513909374582784>",
                            value="All of my modules are currently enabled.\n"
                                  "To enable/disable them use the command: <@457838617633488908> config {module name here} enable/disable\n"
                                  "To see which modules are enabled/disabled use <@457838617633488908> info config\n\n"
                                  "To set custom prefixes and/or remove them, use <@457838617633488908> prefix add/remove {prefix}\n"
                                  "The custom prefix defaults to **!!**")
            try:
                await guild.system_channel.send(embed=embed)
            except:
                await guild.channels[0].send(embed=embed)
            finally:
                with open('guilds.json', 'w') as f:
                    json.dump(guilds, f)
        await logchannel.send(f"```ini\n"
                                                 f"[Guild Name] {guild.name}\n"
                                                 f"[Guild ID] {guild.id}\n"
                                                 f"[Members] {len(guild.members)}\n"
                                                 f"```")

    async def on_member_join(self, member):
        try:
            role = discord.utils.get(member.guild.roles, name='New')
            if role:
                await member.add_roles(role)
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            print('Failed to assign \'New\' role \n{}'.format(exc))

    async def change_status(self):
        await self.wait_until_ready()
        msgs = cycle(status)
        while 1:
            current_status = next(msgs)
            try:
                await self.change_presence(activity=discord.Game(name=current_status))
                await asyncio.sleep(15)
            except Exception as e:
                exc = "{}: {}".format(type(e).__name__, e)
                print('Failed to change status\n{}'.format(exc))

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)


    async def add_guild_permissions(self, guilds, guild: discord.Guild):
        if str(guild.id) not in guilds:
            guilds[str(guild.id)] = {}
            guilds[str(guild.id)]["config"] = True
            guilds[str(guild.id)]["emoji"] = True
            guilds[str(guild.id)]["emojidatabase"] = True
            guilds[str(guild.id)]["exp"] = True
            guilds[str(guild.id)]["lookup"] = True
            guilds[str(guild.id)]["misc"] = True
            guilds[str(guild.id)]["mod"] = True
            guilds[str(guild.id)]["owner"] = True
            guilds[str(guild.id)]["remindme"] = True
            guilds[str(guild.id)]["tags"] = True
            guilds[str(guild.id)]["utilities"] = True
            guilds[str(guild.id)]["stats"] = True
            guilds[str(guild.id)]["fun"] = True
        if str(guild.id) in guilds:
            guilds[str(guild.id)]["config"] = True
            guilds[str(guild.id)]["emoji"] = True
            guilds[str(guild.id)]["emojidatabase"] = True
            guilds[str(guild.id)]["exp"] = True
            guilds[str(guild.id)]["lookup"] = True
            guilds[str(guild.id)]["misc"] = True
            guilds[str(guild.id)]["mod"] = True
            guilds[str(guild.id)]["owner"] = True
            guilds[str(guild.id)]["remindme"] = True
            guilds[str(guild.id)]["tags"] = True
            guilds[str(guild.id)]["utilities"] = True
            guilds[str(guild.id)]["stats"] = True
            guilds[str(guild.id)]["fun"] = True


    def run(self):
        super().run(TOKEN, reconnect=True)


bot = Itachi()
bot.run()








