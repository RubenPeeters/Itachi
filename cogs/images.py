# basic dependencies
import discord
from discord.ext import commands

# aiohttp should be installed if discord.py is
import aiohttp

# PIL can be installed through
# `pip install -U Pillow`
from PIL import Image, ImageDraw, ImageStat, ImageFont

# partial lets us prepare a new function with args for run_in_executor
from functools import partial

# BytesIO allows us to convert bytes into a file-like byte stream.
from io import BytesIO

# this just allows for nice function annotation, and stops my IDE from complaining.
from typing import Union

class ImageCog:
    def __init__(self, bot: commands.Bot):

        # we need to include a reference to the bot here so we can access its loop later.
        self.bot = bot

        # create a ClientSession to be used for downloading avatars
        self.session = aiohttp.ClientSession(loop=bot.loop)

    async def get_average_color(self, image):
        average = ImageStat.Stat(image).median
        color = discord.Color.from_rgb(average[0], average[1], average[2])
        return color


    async def get_avatar(self, user: Union[discord.User, discord.Member]) -> bytes:

        # generally an avatar will be 1024x1024, but we shouldn't rely on this
        avatar_url = user.avatar_url_as(format="png")

        async with self.session.get(avatar_url) as response:
            # this gives us our response object, and now we can read the bytes from it.
            avatar_bytes = await response.read()

        return avatar_bytes

    @staticmethod
    def processing(avatar_bytes: bytes, colour: tuple) -> BytesIO:

        # we must use BytesIO to load the image here as PIL expects a stream instead of
        # just raw bytes.
        with Image.open(BytesIO(avatar_bytes)) as im:

            # this creates a new image the same size as the user's avatar, with the
            # background colour being the user's colour.
            with Image.new("RGB", im.size, colour) as background:

                # this ensures that the user's avatar lacks an alpha channel, as we're
                # going to be substituting our own here.
                rgb_avatar = im.convert("RGB")

                # this is the mask image we will be using to create the circle cutout
                # effect on the avatar.
                with Image.new("L", im.size, 0) as mask:

                    # ImageDraw lets us draw on the image, in this instance, we will be
                    # using it to draw a white circle on the mask image.
                    mask_draw = ImageDraw.Draw(mask)

                    # draw the white circle from 0, 0 to the bottom right corner of the image
                    mask_draw.ellipse([(0, 0), im.size], fill=255)

                    # paste the alpha-less avatar on the background using the new circle mask
                    # we just created.
                    background.paste(rgb_avatar, (0, 0), mask=mask)

                # prepare the stream to save this image into
                final_buffer = BytesIO()

                # save into the stream, using png format.
                background.save(final_buffer, "png")

        # seek back to the start of the stream
        final_buffer.seek(0)

        return final_buffer

    @commands.command()
    async def circle(self, ctx, *, member: discord.Member = None):
        """Display the user's avatar on their colour."""

        # this means that if the user does not supply a member, it will default to the
        # author of the message.
        member = member or ctx.author

        async with ctx.typing():
            # this means the bot will type while it is processing and uploading the image

            if isinstance(member, discord.Member):
                # get the user's colour, pretty self explanatory
                member_colour = member.colour.to_rgb()
            else:
                # if this is in a DM or something went seriously wrong
                member_colour = (0, 0, 0)

            # grab the user's avatar as bytes
            avatar_bytes = await self.get_avatar(member)

            # create partial function so we don't have to stack the args in run_in_executor
            fn = partial(self.processing, avatar_bytes, member_colour)

            # this runs our processing in an executor, stopping it from blocking the thread loop.
            # as we already seeked back the buffer in the other thread, we're good to go
            final_buffer = await self.bot.loop.run_in_executor(None, fn)

            # prepare the file
            file = discord.File(filename="circle.png", fp=final_buffer)

            # send it
            await ctx.send(file=file)

    @commands.command()
    async def color(self, ctx, *, RGB_color: str):
        #if the input is a hex color code
        output_buffer = BytesIO()
        try:
            RGB_color = RGB_color.strip("#")
        except:
            pass
        if len(RGB_color.split(" ")) != 3:
            RGB = tuple(int(RGB_color[i:i + 2], 16) for i in (0, 2, 4))
        else:
            RGB = tuple(map(int, RGB_color.split(" ")))
            RGB_color = '%02x%02x%02x' % RGB
        RGB_forembed = "0x" + RGB_color
        embedcolor = discord.Color(int(RGB_forembed, 0))
        embed = discord.Embed(color=embedcolor)
        image = Image.new("RGB", (256, 256), RGB)
        image.save(output_buffer, "png")
        output_buffer.seek(0)
        embed.set_footer(text=str(RGB) + " #" + RGB_color)
        embed.set_image(url="attachment://color.png")
        file = discord.File(filename="color.png", fp=output_buffer)
        await ctx.send(embed=embed, file=file)

    @commands.command()
    async def avatar(self, ctx, *, member: discord.Member=None):
        member = member or ctx.author
        avatar_bytes = await self.get_avatar(member)
        img = Image.open(BytesIO(avatar_bytes))
        color = await self.get_average_color(img)
        embed = discord.Embed(color=color)
        hex = '#%02x%02x%02x' % color.to_rgb()
        embed.set_footer(text=str(color.to_rgb()) + " " + hex)
        if member is None:
            embed.set_image(url=ctx.author.avatar_url)
        else:
            embed.set_image(url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["bw"])
    async def black_and_white(self, ctx, *, member: discord.Member=None):
        # If no member specified > member = author
        member = member or ctx.author
        output_buffer = BytesIO()
        avatar_bytes = await self.get_avatar(member)
        img = Image.open(BytesIO(avatar_bytes))
        # Convert to black and white
        img = img.convert("L")
        img.save(output_buffer, "png")
        output_buffer.seek(0)
        color = 0xA90000
        embed = discord.Embed(color=color)
        embed.set_image(url="attachment://black_and_white.png")
        file = discord.File(filename="black_and_white.png", fp=output_buffer)
        await ctx.send(embed=embed, file=file)

    @commands.command(aliases=["mlady"])
    async def fedora(self, ctx, *, member: discord.Member=None):
        # If no member specified > member = author
        member = member or ctx.author
        output_buffer = BytesIO()
        avatar_bytes = await self.get_avatar(member)
        img = Image.open(BytesIO(avatar_bytes))
        fedora = Image.open(r'/root/home/itachi/assets/fedora/fedora.png', 'r')
        fedora = fedora.resize(img.size)
        img.paste(fedora, (0, 0), fedora)
        img.save(output_buffer, "png")
        output_buffer.seek(0)
        file = discord.File(filename="test.png", fp=output_buffer)
        await ctx.send(file=file)

    @commands.command()
    async def sickban(self, ctx, *, member: discord.Member = None):
        # If no member specified > member = author
        member = member or ctx.author
        output_buffer = BytesIO()
        avatar_bytes = await self.get_avatar(member)
        img = Image.open(BytesIO(avatar_bytes))
        ban = Image.open(r'/root/home/itachi/assets/ban/ban.png',
                            'r')
        img = img.resize((417, 417))
        ban.paste(img, (60, 334))
        ban.save(output_buffer, "png")
        output_buffer.seek(0)
        file = discord.File(filename="test.png", fp=output_buffer)
        await ctx.send(file=file)

    @commands.command()
    async def trash(self, ctx, *, member: discord.Member = None):
        # If no member specified > member = author
        member = member or ctx.author
        output_buffer = BytesIO()
        avatar_bytes = await self.get_avatar(member)
        img = Image.open(BytesIO(avatar_bytes))
        ban = Image.open(r'/root/home/itachi/assets/trash/trash.png',
                         'r')
        img = img.resize((480, 480))
        ban.paste(img, (480, 0))
        ban.save(output_buffer, "png")
        output_buffer.seek(0)
        file = discord.File(filename="test.png", fp=output_buffer)
        await ctx.send(file=file)

    @commands.command()
    async def abandon(self, ctx, *, text: str = "I dont give Itachi parameters for commands."):
        if len(text) >= 48:
            await ctx.send("the input was too long. (>48 characters)")
            return
        if len(text) >= 24:
            text = text[:24] + '\n' + text[24:]
        output_buffer = BytesIO()
        abandon = Image.open(r'/root/home/itachi/assets/abandon/abandon.png'
                             , 'r')
        draw = ImageDraw.Draw(abandon)
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/arial.ttf', 30)
        draw.text((30, 428), text, (0, 0, 0), font=font)
        abandon.save(output_buffer, "png")
        output_buffer.seek(0)
        file = discord.File(filename="test.png", fp=output_buffer)
        await ctx.send(file=file)





# setup function so this can be loaded as an extension
def setup(bot: commands.Bot):
    bot.add_cog(ImageCog(bot))