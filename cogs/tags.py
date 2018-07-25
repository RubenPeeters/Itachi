import sqlite3
import discord
import discord.ext.commands as commands
from .utils import checks




def setup(bot):
    bot.add_cog(tags(bot))

class tags:
    def __init__(self, bot):
        self.bot = bot
        self.errorchannelid = 467672989232529418



    @commands.group(invoke_without_command=True)
    @checks.is_tags_enabled()
    async def tag(self, ctx, tag: str):
        '''Send text associated with the tag'''
        try:
            conn = sqlite3.connect('itachi.db')
            c = conn.cursor()
            c.execute("SELECT * FROM tags WHERE tag=? AND guild=?",(tag,str(ctx.message.guild)))
            entry = c.fetchone()
            await ctx.send(f"{entry[1]}")
            conn.commit()
            conn.close()
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            await ctx.send('You haven\'t made a `{}` tag'.format(tag,))

    @tag.command()
    @checks.is_tags_enabled()
    async def create(self,ctx, tag:str,*, text :str):
        '''Create a new tag'''
        try:
            conn = sqlite3.connect('itachi.db')
            c = conn.cursor()
            c.execute("SELECT * FROM tags WHERE tag=? AND guild=?", (tag, str(ctx.message.guild)))
            if c.fetchall():
                await ctx.send('There is already a {} tag for this server'.format(tag))
            ### Adding a value to a certain table
            else:
                c.execute("INSERT INTO tags VALUES (?,?,?,?)",(tag,text,str(ctx.message.author),str(ctx.message.guild)))
                conn.commit()
                conn.close()
                await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            await ctx.send('Failed to create tag {}\n{}'.format(tag, exc))

    @tag.command()
    @checks.is_tags_enabled()
    async def remove(self, ctx, tag: str):
        '''Remove a tag by name'''
        try:
            conn = sqlite3.connect('itachi.db')
            c = conn.cursor()
            guild = str(ctx.message.guild)
            ### Adding a value to a certain table
            c.execute("DELETE FROM tags WHERE tag=? AND guild=?",(tag,guild))
            conn.commit()
            conn.close()
            await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            await ctx.send('Failed to remove tag {}\n{}'.format(tag, exc))





