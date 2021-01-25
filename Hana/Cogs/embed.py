import discord
import sys
import os
import io
import re
import asyncio
import json
import ezjson
import textwrap
from discord.ext import commands
from PIL import Image
from urllib import parse

class Embed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Embeds the message
    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def embed(self, ctx, *, msg: str = None):
        t_channel = ctx.message.channel
        async for message in t_channel.history(limit=1):
            if ctx.message.author.id == message.author.id:
                await ctx.message.delete()
                break
        """Embed given text. Ex: Do [p]embed for more help
        Example: [p]embed ptext= word | title=test this | description=some words | color=3AB35E | field=name=test value=test
        You do NOT need to specify every property, only the ones you want.
        **All properties and the syntax:**
        - title=<words>
        - description=<words>
        - color=<hex_value>
        - image=<url_to_image> (must be https)
        - thumbnail=<url_to_image>
        - author=<words> **OR** author=name=<words> icon=<url_to_image>
        - footer=<words> **OR** footer=name=<words> icon=<url_to_image>
        - field=name=<words> value=<words> (you can add as many fields as you want)
        - ptext=<words>
        NOTE: After the command is sent, the bot will delete your message and replace it with the embed. Make sure you have it saved or else you'll have to type it all again if the embed isn't how you want it.
        
        PS: Hyperlink text like so:
        \[text](https://www.whateverlink.com)
        PPS: Force a field to go to the next line with the added parameter inline=False"""
        if msg:
            ptext = title = description = image = thumbnail = color = footer = author = None
            timestamp = discord.Embed.Empty
            embed_values = msg.split('|')
            for i in embed_values:
                if i.strip().lower().startswith('ptext='):
                    ptext = i.strip()[6:].strip()
                elif i.strip().lower().startswith('title='):
                    title = i.strip()[6:].strip()
                elif i.strip().lower().startswith('description='):
                    description = i.strip()[12:].strip()
                elif i.strip().lower().startswith('desc='):
                    description = i.strip()[5:].strip()
                elif i.strip().lower().startswith('image='):
                    image = i.strip()[6:].strip()
                elif i.strip().lower().startswith('thumbnail='):
                    thumbnail = i.strip()[10:].strip()
                elif i.strip().lower().startswith('colour='):
                    color = i.strip()[7:].strip()
                elif i.strip().lower().startswith('color='):
                    color = i.strip()[6:].strip()
                elif i.strip().lower().startswith('footer='):
                    footer = i.strip()[7:].strip()
                elif i.strip().lower().startswith('author='):
                    author = i.strip()[7:].strip()
                elif i.strip().lower().startswith('timestamp'):
                    timestamp = ctx.message.created_at
                else:
                    if description is None and not i.strip().lower().startswith('field='):
                        description = i.strip()

            if color:
                if color.startswith('#'):
                    color = color[1:]
                if not color.startswith('0x'):
                    color = '0x' + color

            if ptext is title is description is image is thumbnail is color is footer is author is None and 'field=' not in msg:
                return await ctx.send(content=None,
                                                    embed=discord.Embed(description=msg))

            if color:
                em = discord.Embed(timestamp=timestamp, title=title, description=description, color=int(color, 16))
            else:
                em = discord.Embed(timestamp=timestamp, title=title, description=description)
            for i in embed_values:
                if i.strip().lower().startswith('field='):
                    field_inline = True
                    field = i.strip().lstrip('field=')
                    field_name, field_value = field.split('value=')
                    if 'inline=' in field_value:
                        field_value, field_inline = field_value.split('inline=')
                        if 'false' in field_inline.lower() or 'no' in field_inline.lower():
                            field_inline = False
                    field_name = field_name.strip().lstrip('name=')
                    em.add_field(name=field_name, value=field_value.strip(), inline=field_inline)
            if author:
                if 'icon=' in author:
                    text, icon = author.split('icon=')
                    if 'url=' in icon:
                        em.set_author(name=text.strip()[5:], icon_url=icon.split('url=')[0].strip(), url=icon.split('url=')[1].strip())
                    else:
                        em.set_author(name=text.strip()[5:], icon_url=icon)
                else:
                    if 'url=' in author:
                        em.set_author(name=author.split('url=')[0].strip()[5:], url=author.split('url=')[1].strip())
                    else:
                        em.set_author(name=author)

            if image:
                em.set_image(url=image)
            if thumbnail:
                em.set_thumbnail(url=thumbnail)
            if footer:
                if 'icon=' in footer:
                    text, icon = footer.split('icon=')
                    em.set_footer(text=text.strip()[5:], icon_url=icon)
                else:
                    em.set_footer(text=footer)
            await ctx.send(content=ptext, embed=em)
        else:
            embed=discord.Embed(
                description="use this website!\nhttps://robyul.chat/embed-creator",
                colour=0xfffafa,
            )
            embed.add_field(name="usage",value="go do everything, then go to the bottom, and click on the `copy` button!",inline=False)
            embed.set_author(name="embed creator!",url="https://robyul.chat/embed-creator")
            embed.add_field(name="what about #channel?",value="remove that! it destroys the whole thing - think of it as this: even if you put the channel name it would **not** send it to the channel! ||im working on it||",inline=False)
            msg = '```How to use the >embed command:\nExample: >embed title=test this | description=some words | color=3AB35E | field=name=test value=test\n\nYou do NOT need to specify every property, only the ones you want.' \
                  '\nAll properties and the syntax (put your custom stuff in place of the <> stuff):\ntitle=<words>\ndescription=<words>\ncolor=<hex_value>\nimage=<url_to_image> (must be https)\nthumbnail=<url_to_image>\nauthor=<words> **OR** author=name=<words> icon=<url_to_image>\nfooter=<words> ' \
                  '**OR** footer=name=<words> icon=<url_to_image>\nfield=name=<words> value=<words> (you can add as many fields as you want)\nptext=<words>\n\nNOTE: After the command is sent, the bot will delete your message and replace it with ' \
                  'the embed. Make sure you have it saved or else you\'ll have to type it all again if the embed isn\'t how you want it.\nPS: Hyperlink text like so: [text](https://www.whateverlink.com)\nPPS: Force a field to go to the next line with the added parameter inline=False```'
            await ctx.send(embed=embed)

def setup(bot): 
    bot.add_cog(embed(bot))  
