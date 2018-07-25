import discord
from discord.ext import commands
import json
import os



async def check_cogs_enabled(ctx: commands.Context, cog: str):
    os.chdir(r'/root/home/itachi')
    with open('guilds.json', 'r') as f:
        guilds = json.load(f)
    return guilds[str(ctx.guild.id)][cog] or ctx.author.id == 150907968068648960

def is_emoji_enabled():
    async def pred(ctx):
        return await check_cogs_enabled(ctx, "emoji")
    return commands.check(pred)

def is_emojidatabase_enabled():
    async def pred(ctx):
        return await check_cogs_enabled(ctx, "emojidatabase")
    return commands.check(pred)

def is_exp_enabled():
    async def pred(ctx):
        return await check_cogs_enabled(ctx, "exp")
    return commands.check(pred)

def is_lookup_enabled():
    async def pred(ctx):
        return await check_cogs_enabled(ctx, "lookup")
    return commands.check(pred)

def is_misc_enabled():
    async def pred(ctx):
        return await check_cogs_enabled(ctx, "misc")
    return commands.check(pred)

def is_mod_enabled():
    async def pred(ctx):
        return await check_cogs_enabled(ctx, "mod")
    return commands.check(pred)

def is_music_enabled():
    async def pred(ctx):
        return await check_cogs_enabled(ctx, "music")
    return commands.check(pred)

def is_owner_enabled():
    async def pred(ctx):
        return await check_cogs_enabled(ctx, "owner")
    return commands.check(pred)

def is_remindme_enabled():
    async def pred(ctx):
        return await check_cogs_enabled(ctx, "remindme")
    return commands.check(pred)

def is_tags_enabled():
    async def pred(ctx):
        return await check_cogs_enabled(ctx, "tags")
    return commands.check(pred)



