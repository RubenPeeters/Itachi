from discord.ext import commands
import discord
import json
import os


def setup(bot):
    bot.add_cog(config(bot))

class config:
    def __init__(self, bot):
        self.bot = bot
        self.errorchannelid = 467672989232529418

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def config(self, ctx, cog: str, param: str):
        '''Configurate the cogs for this server'''
        os.chdir(r'/root/home/itachi')
        with open('guilds.json', 'r') as f:
            guilds = json.load(f)
        await ctx.message.add_reaction('\N{HOURGLASS}')
        if cog != "all":
            if cog in guilds[str(ctx.guild.id)]:
                if cog == "config":
                    await ctx.send("You cannot enable or disable the config module")
                    await ctx.message.remove_reaction('\N{HOURGLASS}', ctx.me)
                    await ctx.message.add_reaction('\N{CROSS MARK}')
                else:
                    if param == "enable" or param == "en":
                        guilds[str(ctx.guild.id)][cog] = True
                        await ctx.send("`{} has succesfully been enabled!`".format(cog))
                        await ctx.message.remove_reaction('\N{HOURGLASS}', ctx.me)
                        await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')
                    if param == "disable" or param == "dis":
                        guilds[str(ctx.guild.id)][cog] = False
                        await ctx.send("`{} has succesfully been disabled!`".format(cog))
                        await ctx.message.remove_reaction('\N{HOURGLASS}', ctx.me)
                        await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')
            else:
                await ctx.send("There is no such module")
                await ctx.message.remove_reaction('\N{HOURGLASS}', ctx.me)
                await ctx.message.add_reaction('\N{CROSS MARK}')
        elif cog == "all":
            cogs_enabled_string = ""
            if param == "enable" or param == "en":
                embed = discord.Embed(name="\u200b")
                for x in guilds[str(ctx.guild.id)]:
                    guilds[str(ctx.guild.id)][x] = True
                    cogs_enabled_string += ":ballot_box_with_check: : " + str(x) + " has succesfully been enabled!\n"
                embed.add_field(name="Cogs", value=cogs_enabled_string)
                await ctx.message.remove_reaction('\N{HOURGLASS}', ctx.me)
                await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')
                await ctx.send(embed=embed)
            if param == "disable" or param == "dis":
                await ctx.send("You can't disable all cogs")
                await ctx.message.remove_reaction('\N{HOURGLASS}', ctx.me)
                await ctx.message.add_reaction('\N{CROSS MARK}')

        with open('guilds.json', 'w') as f:
            json.dump(guilds, f)


