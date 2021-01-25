import discord
import random
import asyncio
import time
import os
from discord import CategoryChannel
from discord.ext import commands, flags
from datetime import date
import string
import json

def config(filename: str = "config"):
    """ Fetch default config file """
    try:
        with open(f"config.json", encoding='utf8') as data:
            return json.load(data)
    except FileNotFoundError:
        raise FileNotFoundError("JSON file wasn't found")

config = config()
##"logging": "insert-the-logging-channel-server-joins"
chars = string.ascii_letters + string.digits + './'

intents = discord.Intents.all()

client = commands.Bot(command_prefix=commands.when_mentioned_or(config["prefix"]),intents=intents)
client.remove_command('help')

from Cogs import timeup
client.add_cog(timeup.Timeup(client))
from Cogs import embed
client.add_cog(embed.Embed(client))

today = date.today()
d2 = today.strftime("%b %d, %Y")

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=config["activity"]))
    print('Logged in as')
    print(client.user)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    guild_ids = open('servers.txt').read().split('\n')
    if message.author == client.user:
        return
    if message.author.bot == True:
        return
    if str(message.guild.id) not in guild_ids:
        return
    try:
        channel_ids = open('whitelist.txt').read().split('\n')
        permission = message.author.guild_permissions.administrator
        if str(message.channel.id) not in channel_ids and permission is False:
            return
        else:
            await client.process_commands(message)
    except Exception as e:
        print(e)

@client.event
async def on_guild_join(guild):
    audit_channel = await client.fetch_channel(config["logging"])
    embed = discord.Embed(title='Server added', type='rich', color=0x2ecc71) #Green
    embed.set_thumbnail(url=guild.icon_url)
    embed.add_field(name='Name', value=guild.name, inline=True)
    embed.add_field(name='ID', value=guild.id, inline=True)
    embed.add_field(name='Owner', value=f'{guild.owner} <@!{guild.owner.id}> ({guild.owner.id})', inline=True)
    embed.add_field(name='Region', value=guild.region, inline=True)
    embed.add_field(name='Members', value=guild.member_count, inline=True)
    embed.add_field(name='Created on', value=guild.created_at, inline=True)
    await audit_channel.send(embed=embed)

@client.event
async def on_guild_remove(guild):
    audit_channel = await client.fetch_channel(config["logging"])
    embed = discord.Embed(title='Server removed', type='rich', color=0xe74c3c) #Red
    embed.set_thumbnail(url=guild.icon_url)
    embed.add_field(name='Name', value=guild.name, inline=True)
    embed.add_field(name='ID', value=guild.id, inline=True)
    embed.add_field(name='Owner', value=f'{guild.owner} <@!{guild.owner.id}> ({guild.owner.id})', inline=True)
    embed.add_field(name='Region', value=guild.region, inline=True)
    embed.add_field(name='Members', value=guild.member_count, inline=True)
    embed.add_field(name='Created on', value=guild.created_at, inline=True)
    await audit_channel.send(embed=embed)

@client.command()
async def servers(ctx):
    if ctx.message.author.id in [336488849217945600,533667968505217024,711482369110179863]:
        async with ctx.typing():
            await asyncio.sleep(1)
        servers = list(client.guilds)
        embed=discord.Embed(
            title=f"Connected on {str(len(servers))} servers:",
            color=0x89CFF0
        )
        for server in servers:
            embed.add_field(name=server.name,value=server.id,inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send("no")

@client.command()
async def leaveme(ctx,server_name=None):
    if ctx.message.author.id in [336488849217945600,533667968505217024,711482369110179863]:
        try:
            if server_name is None:
                server_name = ctx.guild.id
                if ctx.guild.id in [740721211331313726, 552435462451625984]:
                    embed=discord.Embed(
                        description="none can do",
                        color=0x89CFF0,
                    )
                    await ctx.send(embed=embed)
                    return
            server_id = int(server_name)
            toleave = client.get_guild(server_id)
            embed=discord.Embed(
                description=f"leaving {toleave.name}",
                color=0x89CFF0,
            )
            async with ctx.typing():
                await asyncio.sleep(3)
            await ctx.send(embed=embed)
            await toleave.leave()
        except:
            embed=discord.Embed(
                color=0x89CFF0,
                description="non a server",
            )
            async with ctx.typing():
                await asyncio.sleep(3)
            await ctx.send(embed=embed)
    else:
        return

#@client.command()
# async def inviteinfo(ctx, invite: discord.Invite):
#member = discord.utils.get(client.get_all_members(), id=PUT ID HERE))

@client.command()
@commands.has_permissions(administrator=True)
async def check(ctx):
    ch = open("checkinvites.txt").read()
    bl_channels = tuple(open("channel_blacklist.txt").read().split("\n"))
    
    if str(ctx.guild.id) in ch:
        if str(ctx.message.channel.id) in ch:
            categories = open("category_id.txt").read().split("\n")
            guild_categories = [str(cat.id) for cat in ctx.guild.categories]
            await ctx.channel.purge(limit=10000)
            embe=discord.Embed(
                description=f"An invite check is currently in process. Please wait a few minute as {client.user.name} searches your categories.",
                colour=0xfffafa,
            )
            await ctx.send(embed=embe)
            category_ids = []

            for i in guild_categories:
                if i in categories:
                    category_ids.append(i)

            channel_count = 0
            inv_count = 0
            good_inv = 0 
            bad_inv = 0

            for cat_id in category_ids:
                try:
                    endstring = ''
                    category = client.get_channel(int(cat_id))

                    for channel in category.text_channels:
                        if str(channel.id) in bl_channels: continue
                        channel_count += 1
                        total_invites = 0
                        valid_invites = 0
                        h = await channel.history(limit=10).flatten()

                        for msg in h:
                            content = msg.content
                            if 'discord.gg' in msg.content:
                                link = ''
                                link_index = content.index("discord.gg")
                                for char in content[link_index:]:
                                    if char in chars:
                                        link += char
                                    else:
                                        break
                                link = "https://" + link
                                total_invites += 1
                                inv_count += 1

                                try:
                                    invite = await client.fetch_invite(link)
                                    user = int(invite.approximate_member_count)
                                    valid_invites += 1
                                    good_inv += 1
                                except discord.NotFound:
                                    bad_inv += 1
                                    pass
                                
                        if total_invites!= 0:
                            if valid_invites != total_invites:
                                emoji = ":red_circle:"
                                status = "bad"
                                users = "0"
                            else:
                                emoji = ":green_circle:"
                                status = 'good'
                                users = user
                            endstring += f"{emoji} {channel.mention} : {valid_invites}/{total_invites} {status} `{users} Users`\n"
                           # endstring += f"{emoji} {valid_invites}/{total_invites} {status}\n" 
                        else:
                            endstring += f":red_circle: {channel.mention} : 0 found `0 Users`\n"
                    
                    if endstring == "":
                        endstring = "No channels found."

                    if len(endstring) <= 1024:
                        embed = discord.Embed(
                            title=f"The {category.name} category",
                            description=endstring,
                            colour=0xfffafa,
                        )
                        if endstring != "": embed.set_footer(text = f"Checked 10 recent messages・{d2}")

                        await ctx.send(embed=embed)
                    else:
                        endstringlines = endstring.split('\n')
                        endstring1 = '\n'.join(endstringlines[:len(endstringlines)//2])
                        endstring2 = '\n'.join(endstringlines[len(endstringlines)//2:])

                        embed1 = discord.Embed(
                            title=f"The {category.name} category",
                            description=endstring1,
                            colour=0xfffafa,
                        )
                        embed2 = discord.Embed(
                            title=f"The {category.name} category",
                            description=endstring2,
                            colour=0xfffafa,
                        )

                        await ctx.send(embed=embed1)
                        await ctx.send(embed=embed2)

                    
                except ValueError:
                    pass

            final_embed = discord.Embed(
                description=f"Invite check complete!",
                colour=0x15ff00,
            )
            
            goood = (good_inv/inv_count)*100
            baaad = (bad_inv/inv_count)*100

            #formatted_float = "{:.2f}".format(a_float)

            goooood = "{:.2f}".format(goood)
            baaaaad = "{:.2f}".format(baaad)


            total = discord.Embed(
                title="Invite check results",
                colour=0xfffafa,
            )
            total.add_field(name="Check counts",value=f"Channels checked: {channel_count}\nInvites checked: {inv_count}",inline=False)
            total.add_field(name="Stats",value=f"- {good_inv}/{inv_count} good invites ({goooood}% :green_circle:)\n- {bad_inv}/{inv_count} bad invites ({baaaaad}% :red_circle:)")


            await ctx.send(embed=final_embed)
            await ctx.send(embed=total)
            
        else:
            for i in ch.split('\n'):
                if i.split(' : ')[0] == str(ctx.guild.id):
                    channel_id = i.split(' : ')[1]
                    break

            embed = discord.Embed(
                description= f"The `check` command will only work in <#{channel_id}>"
            )
            await ctx.send(embed=embed)
    else:
        embed=discord.Embed(
            description="This server didn't register a channel. Run `::checkchannel <#channel>` to add a channel for invite checking.",
            color=0xd80000,
        )
        await ctx.send(embed=embed)
@check.error
async def check(ctx,error):
    print(error)

    
@client.command()
@commands.has_permissions(administrator=True)
async def category(ctx, cmd, category_id=None):
    
    if cmd == "add" and category_id is not None:
        category = client.get_channel(int(category_id))
        category_ids = open("category_id.txt").read().split('\n')
        if category_id in category_ids:
            embed=discord.Embed(
                description=f"{category.name} is already in the list.",
                color=0xd80000
            )
            await ctx.send(embed=embed)
        else:
            with open("category_id.txt",'a') as f:
                f.write(str(category_id)+'\n')
            embed=discord.Embed(
                description=f"{category.name} is added into the list.",
                color=0x14eb14
            )
            await ctx.send(embed=embed)
    
    elif cmd in ['rm','remove'] and category_id is not None:
        category = client.get_channel(int(category_id))
        category_ids = open("category_id.txt").read().split('\n')
        if category_id not in category_ids:
            embed=discord.Embed(
                description="No category was found. Try using the category ID.",
                color=0xd80000
            )
            await ctx.send(embed=embed)
        
        else:
            category_ids.remove(category_id)
            with open("category_id.txt",'w') as f:
                f.write('\n'.join(category_ids)+'\n')
            embed=discord.Embed(
                description=f"{category.name} was removed from the list.",
                color=0x14eb14
            )
            await ctx.send(embed=embed)
            
    elif cmd == "list":
        category_ids = open('category_id.txt').read().split('\n')
        description = ""
        guild_category_ids = [i.id for i in ctx.guild.categories]

        for ch_id in category_ids:
            if ch_id != "":
                if int(ch_id) in guild_category_ids:
                    category = client.get_channel(int(ch_id))
                    description += f"{category.name}\n"

        if description == "":
            description = "No categories found."
            
        embed=discord.Embed(
            title=f"{ctx.guild.name}'s categories",
            description=description
        )
        await ctx.send(embed=embed)
        
    else:
        embed=discord.Embed(
            description="Command not found. Try using `add` to add categories and `remove` to remove categories.",
            color=0x14eb14,
        )
        await ctx.send(embed=embed)
@category.error
async def category_error(ctx,error):
    if isinstance(error,commands.BadArgument):
        embed=discord.Embed(
            description=f"No channel was found. Try using the category ID.",
            color=0x14eb14,
        )
        await ctx.send(embed=embed)
    else:
        print(error)

@client.command()
@commands.has_permissions(administrator=True)
async def ignore(ctx, cmd, channel:discord.TextChannel = None):
    fn = "channel_blacklist.txt"
    
    if channel is not None: channel_id = str(channel.id)
    else: channel_id = None
    if fn not in os.listdir():
        file = open("channel_blacklist.txt",'w')
        file.close()

    if cmd == "add" and channel is not None:
        channel_ids = open(fn).read().split('\n')
        if channel_id in channel_ids:
            embed=discord.Embed(
                description=f"{channel.mention} is already in the blacklist.",
                color=0xd80000
            )
            await ctx.send(embed=embed)
        else:
            with open(fn,'a') as f:
                f.write(channel_id+'\n')
            embed=discord.Embed(
                description=f"{channel.mention} is added into the blacklist.",
                color=0x14eb14
            )
            await ctx.send(embed=embed)

    elif cmd in ['rm','remove'] and channel is not None:
        channel_ids = open(fn).read().split('\n')
        if channel_id not in channel_ids:
            embed=discord.Embed(
                description="No channel was found. Try using #channel.",
                color=0xd80000
            )
            await ctx.send(embed=embed)
        
        else:
            channel_ids.remove(channel_id)
            with open(fn,'w') as f:
                f.write('\n'.join(channel_ids)+'\n')
            embed=discord.Embed(
                description=f"{channel.mention} was removed from the blacklist.",
                color=0x14eb14
            )
            await ctx.send(embed=embed)

    elif  cmd == "list":
        channel_ids = open(fn).read().split('\n')
        description = ""
        
        guild_category_ids = [i.id for i in ctx.guild.text_channels]

        for ch_id in channel_ids:
            if ch_id != "":
                if int(ch_id) in guild_category_ids:
                    description += f"<#{ch_id}>\n"

        if description == "":
            description = "No categories found."
        
        embed = discord.Embed(
            title=f"{ctx.guild.name} blacklisted channels",
            description= description
        )
        await ctx.send(embed=embed)
    
    else:
        embed=discord.Embed(
            description="Command not found. Try using `add` to add channels and `remove` to remove channels.",
            color=0xd80000,
        )
        await ctx.send(embed=embed)
@ignore.error
async def ignore_error(ctx,error):
    if isinstance(error,commands.BadArgument):
        embed=discord.Embed(
            description=f"No channel was found. Try using #channel.",
            color=0xd80000,
        )
        await ctx.send(embed=embed)
    else:
        print(error)

@client.command()
@commands.has_permissions(administrator=True)
async def bots(ctx, cmd, channel:discord.TextChannel = None):
    fn = "whitelist.txt"
    
    if channel is not None: channel_id = str(channel.id)
    else: channel_id = None
    if fn not in os.listdir():
        file = open("whitelist.txt",'w')
        file.close()

    if cmd == "add" and channel is not None:
        channel_ids = open(fn).read().split('\n')
        if channel_id in channel_ids:
            embed=discord.Embed(
                description=f"{channel.mention} is already in the whitelist.",
                color=0xd80000
            )
            await ctx.send(embed=embed)
        else:
            with open(fn,'a') as f:
                f.write(channel_id+'\n')
            embed=discord.Embed(
                description=f"{channel.mention} is added into the whitelist.",
                color=0x14eb14
            )
            await ctx.send(embed=embed)

    elif cmd in ['rm','remove'] and channel is not None:
        channel_ids = open(fn).read().split('\n')
        if channel_id not in channel_ids:
            embed=discord.Embed(
                description="No channel was found. Try using #channel.",
                color=0xd80000
            )
            await ctx.send(embed=embed)
        
        else:
            channel_ids.remove(channel_id)
            with open(fn,'w') as f:
                f.write('\n'.join(channel_ids)+'\n')
            embed=discord.Embed(
                description=f"{channel.mention} was removed from the whitelist.",
                color=0x14eb14
            )
            await ctx.send(embed=embed)

    elif  cmd == "list":
        channel_ids = open(fn).read().split('\n')
        description = ""
        
        guild_category_ids = [i.id for i in ctx.guild.text_channels]

        for ch_id in channel_ids:
            if ch_id != "":
                if int(ch_id) in guild_category_ids:
                    description += f"<#{ch_id}>\n"

        if description == "":
            description = "No categories found."
        
        embed = discord.Embed(
            title=f"{ctx.guild.name} whitelisted channels",
            description= description
        )
        await ctx.send(embed=embed)
    
    else:
        embed=discord.Embed(
            description="Command not found. Try using `add` to add channels and `remove` to remove channels.",
            color=0xd80000,
        )
        await ctx.send(embed=embed)
@bots.error
async def bots_error(ctx,error):
    if isinstance(error,commands.BadArgument):
        embed=discord.Embed(
            description=f"No channel was found. Try using #channel.",
            color=0xd80000,
        )
        await ctx.send(embed=embed)
    else:
        print(error)

@client.command()
async def checkchannel(ctx, channel:discord.TextChannel):
    file_dir = 'checkinvites.txt'
    
    if file_dir not in os.listdir():
        file = open(file_dir,'w')
        file.close()

    channels = open(file_dir).read()
    if str(ctx.guild.id) in channels:
        channels_list = channels.split('\n')
        for i in range(len(channels_list)):
            if channels_list[i].split(' : ')[0] == str(ctx.guild.id):
                channels_list[i] = f"{ctx.guild.id} : {channel.id}"

        string = '\n'.join(channels_list)
        with open(file_dir,'w') as f:
            f.write(string)

    else:
        string = f"{channels}\n{ctx.guild.id} : {channel.id}"
        with open(file_dir,'w') as f:
            f.write(string)

    embed=discord.Embed(
        description=f"Invite check channel changed to {channel.mention}.",
        color=0x14eb14
    )
    await ctx.send(embed=embed)

@client.command()
async def ids(ctx):
    categories = ctx.guild.categories
    divided_categories = [categories[i:i+5] for i in range(0, len(categories), 5)]

    embed = discord.Embed(
        title=f"{ctx.guild.name}'s categories",
        colour=0xfffafa,
    )

    x = 1
    for y in divided_categories:
        value = ''
        for category in y:
            value += f"**{category.name}** - `{category.id}`\n"

        if x != (x+len(y)-1):
            embed.add_field(name=f"Categories {x} - {x+len(y)-1}",value=value,inline=False)
        else:
            embed.add_field(name=f"Categories {x}",value=value,inline=False)
        x += len(y)
    await ctx.send(embed=embed)

@client.command()
@commands.has_permissions(administrator=True)
async def server(ctx, cmd, guild = None):
    fn = "servers.txt"
    
    if guild is not None: guild_id = str(guild)
    else: guild_id = None
    if fn not in os.listdir():
        file = open("servers.txt",'w')
        file.close()

    if cmd == "add" and guild is not None:
        guild_ids = open(fn).read().split('\n')
        if guild_id in guild_ids:
            embed=discord.Embed(
                description=f"{guild_id} is already in the whitelist.",
                color=0xd80000
            )
            await ctx.send(embed=embed)
        else:
            with open(fn,'a') as f:
                f.write(guild_id+'\n')
            embed=discord.Embed(
                description=f"{guild_id} is added into the whitelist.",
                color=0x14eb14
            )
            await ctx.send(embed=embed)

    elif cmd in ['rm','remove'] and guild is not None:
        guild_ids = open(fn).read().split('\n')
        if guild_id not in guild_ids:
            embed=discord.Embed(
                description="No guild was found. Try using the exact guildid.",
                color=0xd80000
            )
            await ctx.send(embed=embed)
        
        else:
            guild_ids.remove(guild_id)
            with open(fn,'w') as f:
                f.write('\n'.join(guild_ids)+'\n')
            embed=discord.Embed(
                description=f"{guild_id} was removed from the whitelist.",
                color=0x14eb14
            )
            await ctx.send(embed=embed)

    elif  cmd == "list":
        guild_ids = open(fn).read().split('\n')
        description = ""
        guild_ids = open(fn).read().split('\n')
        valid_servers = len(guild_ids)
            
        for gd_id in guild_ids:
            if gd_id != "":
                guilds = client.get_guild(int(gd_id))
                description += f"・{guilds} `{gd_id}`\n"

        if description == "":
            description = "No guilds found."
        
        if len(description) <= 1024:
            embed = discord.Embed(
                title=f"Whitelisted guilds ; {valid_servers} servers",
                description=description,
                colour=0xfffafa,
            )

            await ctx.send(embed=embed)
        else:
            endstringlines = description.split('\n')
            endstring1 = '\n'.join(endstringlines[:len(endstringlines)//2])
            endstring2 = '\n'.join(endstringlines[len(endstringlines)//2:])

            embed1 = discord.Embed(
                title=f"Whitelisted guilds ; {valid_servers} servers",
                description=endstring1,
                colour=0xfffafa,
            )
            embed2 = discord.Embed(
                title=f"Whitelisted guilds ; {valid_servers} servers",
                description=endstring2,
                colour=0xfffafa,
            )

            await ctx.send(embed=embed1)
            await ctx.send(embed=embed2)
    
    else:
        embed=discord.Embed(
            description="Command not found. Try using `add` to add guilds and `remove` to remove guilds.",
            color=0xd80000,
        )
        await ctx.send(embed=embed)
@server.error
async def server_error(ctx,error):
    if isinstance(error,commands.BadArgument):
        embed=discord.Embed(
            description=f"No guild was found. Try using the guild id.",
            color=0xd80000,
        )
        await ctx.send(embed=embed)
    else:
        print(error)

@client.command()
async def guilds(ctx):
    if ctx.message.author.id in [336488849217945600,533667968505217024,711482369110179863]:
        async with ctx.typing():
            await asyncio.sleep(1)
        servers = list(client.guilds)
        description = " "
        for server in servers:
            description += f"・{server.name} `{server.id}`\n"
        embed=discord.Embed(
            title=f"Connected on {str(len(servers))} servers:",
            description=description,
            colour=0xfffafa
        )
        await ctx.send(embed=embed)
    else:
        return

@client.command()
async def support(ctx):
    text = f"> https://discord.gg/NpXt8nwjqf\nJoin the support server for {client.user.name}!"
    await ctx.send(text)

@client.command()
async def checkinvites(ctx):
    embed=discord.Embed(
        description="Try running `::check` instead!",
        colour=0x2f3136
    )
    await ctx.send(embed=embed)

@client.command()
async def help(ctx,cmd = None):
    allowed = [780273853749657600]
    me = [711482369110179863]
    if ctx.guild.id in allowed and ctx.message.author.id in me:
        if cmd == "server":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Uma",inline=False)
            embed.add_field(name="Description",value=f"Modifies the servers allowed to use {client.user.name}",inline=False)
            embed.add_field(name="Usage",value="`::server <add|remove|list> [guildId]`",inline=False)
            embed.add_field(name="Aliases",value="`::server`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "leaveme":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Uma",inline=False)
            embed.add_field(name="Description",value="Leave the guild with the guild id ",inline=False)
            embed.add_field(name="Usage",value="`::leaveme [guildId]`",inline=False)
            embed.add_field(name="Aliases",value="`::leaveme`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "guilds":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Uma",inline=False)
            embed.add_field(name="Description",value=f"Guilds that {client.user.name} is in (total)",inline=False)
            embed.add_field(name="Usage",value="`::guilds`",inline=False)
            embed.add_field(name="Aliases",value="`::guilds`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == None:
            embed=discord.Embed(
                title=f"{client.user.name}'s commands",
                colour=0xfffafa,
            )
            embed.add_field(name="Uma",value=f"・`server` - Modifies servers allowed to use {client.user.name}\n・`guilds` - Guilds that {client.user.name} is in (total)\n・`leaveme` - Leave the guild with the guild id",inline=False)
            embed.add_field(name="Admin",value="・`bots` - Modifies the bot channel list\n・`ignore` - Modifies the channel blacklist\n・`category` - Modifies the category whitelist\n・`ids` - Displays a list of all category IDs in a server\n・`checkchannel` - Modifies the invite check channel",inline=False)
            embed.add_field(name="Invites",value="・`check` - Checks invites from provided category",inline=False)
            embed.add_field(name="Utility",value=f"・`guide` - A guide to {client.user.name}\n・`help` - Displays all available commands, including information about a specific command.in\n・`ping` - Checks server latency\n・`stats` - Displays bot information",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "ignore":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Admin",inline=False)
            embed.add_field(name="Description",value="Modifies the channel blacklist",inline=False)
            embed.add_field(name="Usage",value="`::ignore <add|remove|list> [#channel]`",inline=False)
            embed.add_field(name="Aliases",value="`::ignore`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "bots":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Admin",inline=False)
            embed.add_field(name="Description",value="Modifies the channel whitelist",inline=False)
            embed.add_field(name="Usage",value="`::bots <add|remove|list> [#channel]`",inline=False)
            embed.add_field(name="Aliases",value="`::bots`",inline=False)
            await ctx.send(embed=embed)

        elif cmd == "checkchannel":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Admin",inline=False)
            embed.add_field(name="Description",value="Modifies the invite check channel",inline=False)
            embed.add_field(name="Usage",value="`::checkchannel #channel`",inline=False)
            embed.add_field(name="Aliases",value="`::checkchannel`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "category":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Admin",inline=False)
            embed.add_field(name="Description",value="Modifies the category whitelist",inline=False)
            embed.add_field(name="Usage",value="`::category <add|remove|list> [categoryChannel]`",inline=False)
            embed.add_field(name="Aliases",value="`::category`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "ids":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Admin",inline=False)
            embed.add_field(name="Description",value="Displays a list of all category IDs in a server",inline=False)
            embed.add_field(name="Usage",value="`::ids`",inline=False)
            embed.add_field(name="Aliases",value="`::ids`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "check":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="General",inline=False)
            embed.add_field(name="Description",value="Checks invites from provided categories. Would check for codeblock errors in the channel by default. ",inline=False)
            embed.add_field(name="Usage",value="`::check`",inline=False)
            embed.add_field(name="Aliases",value="`::check`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "guide":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Utility",inline=False)
            embed.add_field(name="Description",value=f"A guide to {client.user.name}",inline=False)
            embed.add_field(name="Usage",value="`::guide`",inline=False)
            embed.add_field(name="Aliases",value="`::guide`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "help":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Utility",inline=False)
            embed.add_field(name="Description",value="Displays all available commands, including information about a specific command. ",inline=False)
            embed.add_field(name="Usage",value="`::help`",inline=False)
            embed.add_field(name="Aliases",value="`::help`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "ping":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Utility",inline=False)
            embed.add_field(name="Description",value="Checks server latency",inline=False)
            embed.add_field(name="Usage",value="`::ping`",inline=False)
            embed.add_field(name="Aliases",value="`::ping`",inline=False)
            await ctx.send(embed=embed)
            
        elif cmd == "stats":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Utility",inline=False)
            embed.add_field(name="Description",value="Displays bot information",inline=False)
            embed.add_field(name="Usage",value="`::stats`",inline=False)
            embed.add_field(name="Aliases",value="`::stats`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "report":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Utility",inline=False)
            embed.add_field(name="Description",value="Reports a bug found to the developers",inline=False)
            embed.add_field(name="Usage",value="`::report <bug>`",inline=False)
            embed.add_field(name="Aliases",value="`::report`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "embed":
            embed=discord.Embed(
                description="use this website!\nhttps://robyul.chat/embed-creator",
                colour=0xfffafa,
            )
            embed.add_field(name="usage",value="go do everything, then go to the bottom, and click on the `copy` button!",inline=False)
            embed.set_author(name="embed creator!",url="https://robyul.chat/embed-creator")
            embed.add_field(name="what about #channel?",value="remove that! it destroys the whole thing - think of it as this: even if you put the channel name it would **not** send it to the channel! ||im working on it||",inline=False)
            await ctx.send(embed=embed)
        else:
            return
    else:
        if cmd == None:
            embed=discord.Embed(
                title=f"{client.user.name}'s commands",
                colour=0xfffafa,
            )    
            embed.add_field(name="Admin",value="・`bots` - Modifies the bot channel list\n・`blacklist` - Modifies the channel blacklist\n・`category` - Modifies the category whitelist\n・`ids` - Displays a list of all category IDs in a server\n・`checkchannel` - Modifies the invite check channel",inline=False)
            embed.add_field(name="Invites",value="・`check` - Checks invites from provided category",inline=False)
            embed.add_field(name="Utility",value=f"・`guide` - A guide to {client.user.name}\n・`help` - Displays all available commands, including information about a specific command.\n・`ping` - Checks server latency\n・`stats` - Displays bot information",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "embed":
            embed=discord.Embed(
                description="use this website!\nhttps://robyul.chat/embed-creator",
                colour=0xfffafa,
            )
            embed.add_field(name="usage",value="go do everything, then go to the bottom, and click on the `copy` button!",inline=False)
            embed.set_author(name="embed creator!",url="https://robyul.chat/embed-creator")
            embed.add_field(name="what about #channel?",value="remove that! it destroys the whole thing - think of it as this: even if you put the channel name it would **not** send it to the channel! ||im working on it||",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "ignore":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Admin",inline=False)
            embed.add_field(name="Description",value="Modifies the channel blacklist",inline=False)
            embed.add_field(name="Usage",value="`::ignore <add|remove|list> [#channel]`",inline=False)
            embed.add_field(name="Aliases",value="`::ignore`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "bots":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Admin",inline=False)
            embed.add_field(name="Description",value="Modifies the channel whitelist",inline=False)
            embed.add_field(name="Usage",value="`::bots <add|remove|list> [#channel]`",inline=False)
            embed.add_field(name="Aliases",value="`::bots`",inline=False)
            await ctx.send(embed=embed)

        elif cmd == "checkchannel":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Admin",inline=False)
            embed.add_field(name="Description",value="Modifies the invite check channel",inline=False)
            embed.add_field(name="Usage",value="`::checkchannel #channel`",inline=False)
            embed.add_field(name="Aliases",value="`::checkchannel`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "category":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Admin",inline=False)
            embed.add_field(name="Description",value="Modifies the category whitelist",inline=False)
            embed.add_field(name="Usage",value="`::category <add|remove|list> [categoryChannel]`",inline=False)
            embed.add_field(name="Aliases",value="`::category`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "ids":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Admin",inline=False)
            embed.add_field(name="Description",value="Displays a list of all category IDs in a server",inline=False)
            embed.add_field(name="Usage",value="`::ids`",inline=False)
            embed.add_field(name="Aliases",value="`::ids`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "check":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="General",inline=False)
            embed.add_field(name="Description",value="Checks invites from provided categories. Would check for codeblock errors in the channel by default. ",inline=False)
            embed.add_field(name="Usage",value="`::check`",inline=False)
            embed.add_field(name="Aliases",value="`::check`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "guide":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Utility",inline=False)
            embed.add_field(name="Description",value=f"A guide to {client.user.name}",inline=False)
            embed.add_field(name="Usage",value="`::guide`",inline=False)
            embed.add_field(name="Aliases",value="`::guide`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "help":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Utility",inline=False)
            embed.add_field(name="Description",value="Displays all available commands, including information about a specific command. ",inline=False)
            embed.add_field(name="Usage",value="`::help`",inline=False)
            embed.add_field(name="Aliases",value="`::help`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "ping":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Utility",inline=False)
            embed.add_field(name="Description",value="Checks server latency",inline=False)
            embed.add_field(name="Usage",value="`::ping`",inline=False)
            embed.add_field(name="Aliases",value="`::ping`",inline=False)
            await ctx.send(embed=embed)
            
        elif cmd == "stats":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Utility",inline=False)
            embed.add_field(name="Description",value="Displays bot information",inline=False)
            embed.add_field(name="Usage",value="`::stats`",inline=False)
            embed.add_field(name="Aliases",value="`::stats`",inline=False)
            await ctx.send(embed=embed)
        else:
            return

@client.command()
async def guide(ctx):
    f1=f'1. By default, {client.user.name} has administrator permissions on its "{client.user.name}" role.'
    f2='・To start (if needed), please have an administrator whitelist channels using the `::bots add <channel>` commands.\n・This is to desinate channels to let users run non-admin commands such as `::help` and `::stats`.\n・Administrators can run commands anywhere on the server; however, everyone else can only run commands in __whitelisted__ channels.\n・Please note that both the `::embed` and `::check` commands can __only__ be run by administrators.'
    f3='1. Set an invite check channel with `::checkchannel [textChannel]`.\n2. Add the category IDs **(one at a time)** to check invites for using `::category add [categoryChannelId]`.\n3. Run `::ids` to see available categories in your portal. \n4. If you have channels that you want to ignore during the invite checks, you can blacklist them using `::ignore add [#channel]`\n5. Run `::check` **(in the invite check channel)** and wait a little bit.\n6. __Invite check complete!__'
    f4='・For some commands, there are three actions - add, remove, and list:\n・**add** - adds the given channel to the list\n・**remove** - removes the given channel from the list\n・**list** - lists the current channels saved in the list\n・The help command is `::help`\n・For issues, message Uma#0001'
    embed=discord.Embed(
        title=f"A guide to {client.user.name}",
        colour=0xfffafa,
    )
    embed.add_field(name="Things to know before you start",value=f1,inline=False)
    embed.add_field(name="Setup",value=f2,inline=False)
    embed.add_field(name="Invite checks",value=f3,inline=False)
    embed.add_field(name="Useful stuff",value=f4,inline=False)
    await ctx.send(embed=embed)
            
client.run(config["token"])
        
