import discord
import random
import asyncio
import time
import os
from dotenv import load_dotenv
from discord import CategoryChannel
from discord.ext import commands
from datetime import date
import string
import json
import keep_alive

load_dotenv()

def config(filename: str = "config"):
    """ Fetch default config file """
    try:
        with open(f"config.json", encoding='utf8') as data:
            return json.load(data)
    except FileNotFoundError:
        raise FileNotFoundError("Json file wasn't found :(")

token = os.getenv("DISCORD_TOKEN")
chars = string.ascii_letters + string.digits + './'
intents = discord.Intents.all()
prefix = config()["prefix"]
client = commands.Bot(command_prefix=commands.when_mentioned_or(prefix),intents=intents)
client.remove_command('help')

from Cogs import timeup
client.add_cog(timeup.Timeup(client))
from Cogs import embed
client.add_cog(embed.Embed(client))

today = date.today()
d2 = today.strftime("%b %d, %Y")
act = config()["activity"]

@client.event
async def on_ready():
    prefix = config()["prefix"]
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=f"{act} | {prefix}guide"))
    print('Logged in as')
    print(client.user)
    print(client.user.id)
    print('------')

@client.event
async def on_command_error(ctx,error):
    print(error)

@client.event
async def on_message(message):
    guild_ids = open('servers.txt').read().split('\n')
    main_server = config()["server"]
    if message.author == client.user:
        return
    if message.author.bot == True:
        return
    if str(message.guild.id) not in guild_ids and str(message.guild.id) not in main_server:
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
    logging = config()["logging"]
    audit_channel = await client.fetch_channel(logging)
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
    logging = config()["logging"]
    audit_channel = await client.fetch_channel(logging)
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
async def leaveme(ctx,server_name=None):
    #os.getenv
    #logging = config()["logging"]
    owners = config()["owners"]
    main_server = config()["server"]
    if str(ctx.author.id) in owners:    
        try:
            if server_name is None:
                server_name = ctx.guild.id
                if str(ctx.guild.id) in main_server:
                    embed=discord.Embed(
                        description="You can't leave your main server.",
                        color=0xe74d3f,
                    )
                    await ctx.send(embed=embed)
                    return
            server_id = int(server_name)
            toleave = client.get_guild(server_id)
            embed=discord.Embed(
                description=f"Leaving {toleave.name}",
                color=0x2fcc78,
            )
            await ctx.send(embed=embed)
            await toleave.leave()
        except:
            embed=discord.Embed(
                color=0xe74d3f,
                description="Not a server.",
            )
            await ctx.send(embed=embed)
    else:
        return

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
        prefix = config()["prefix"]
        embed=discord.Embed(
            description=f"This server didn't register a channel. Run `{prefix}checkchannel <#channel>` to add a channel for invite checking.",
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
async def server(ctx, cmd, guild = None):
    owners = config()["owners"]
    if str(ctx.author.id) in owners:
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
    else:
        return
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
    owners = config()["owners"]
    if str(ctx.author.id) in owners:
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
async def checkinvites(ctx):
    prefix = config()["prefix"]
    embed=discord.Embed(
        description=f"Try running `{prefix}check` instead!",
        colour=0x2f3136
    )
    await ctx.send(embed=embed)

@client.command()
@commands.guild_only()
async def prefix(ctx):
    prefix = config()["prefix"]
    embed=discord.Embed(
        description=f"Current prefix is `{prefix}`",
        colour=0xfffafa
    )
    await ctx.send(embed=embed)

@client.command()
async def invid(ctx, invite: discord.Invite):
    owners = config()["owners"]
    if str(ctx.author.id) in owners:
        invite = await client.fetch_invite(invite)
        guild = invite.guild
        code = invite.code
        embed=discord.Embed(
            title="Invite information",
            description=f"Code ⸝⸝ {code}\nServer ⸝⸝ {guild}\nServer ID ⸝⸝ {guild.id}",
            colour=0xfffafa,
        )
        embed.set_thumbnail(url=guild.icon_url)
        await ctx.send(embed=embed)
    else:
        return
@invid.error
async def invid_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        embed=discord.Embed(
            title="Invalid Invite",
            description="That invite is invalid or has expired.",
            color=0xe64e43,
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed=discord.Embed(
            title="Invalid Invite",
            description="That is not an invite.",
            color=0xe64e43,
        )
        await ctx.send(embed=embed)
    else:
        print(error)

@client.command()
async def help(ctx,cmd = None):
    owners = config()["owners"]
    prefix = config()["prefix"] #{prefix}
    if str(ctx.author.id) in owners:
        if cmd == "server":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Owner",inline=False)
            embed.add_field(name="Description",value=f"Modifies the servers allowed to use {client.user.name}",inline=False)
            embed.add_field(name="Usage",value=f"`{prefix}server <add|remove|list> [guildId]`",inline=False)
            embed.add_field(name="Aliases",value=f"`{prefix}server`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "leaveme":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Owner",inline=False)
            embed.add_field(name="Description",value="Leave the guild with the guild id ",inline=False)
            embed.add_field(name="Usage",value=f"`{prefix}leaveme [guildId]`",inline=False)
            embed.add_field(name="Aliases",value=f"`{prefix}leaveme`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "guilds":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Owner",inline=False)
            embed.add_field(name="Description",value=f"Guilds that {client.user.name} is in (total)",inline=False)
            embed.add_field(name="Usage",value=f"`{prefix}guilds`",inline=False)
            embed.add_field(name="Aliases",value=f"`{prefix}guilds`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == None:
            embed=discord.Embed(
                title=f"{client.user.name}'s commands",
                description=f"Here's the list of available commands. For more specific and detailed help for each commands, use `{prefix}help [command]` like `{prefix}help check`.\nBot prefix: `{prefix}`, <@{client.user.id}>\n\nAvailable Commands: 14",
                colour=0xfffafa,
            )
            embed.add_field(name="Owner",value=f"・`server` - Modifies servers allowed to use {client.user.name}\n・`guilds` - Guilds that {client.user.name} is in (total)\n・`leaveme` - Leave the guild with the guild id\n・`invid` - Shows you the server id of the invite provided",inline=False)
            embed.add_field(name="Admin",value="・`bots` - Modifies the bot channel list\n・`ignore` - Modifies the channel blacklist\n・`category` - Modifies the category whitelist\n・`ids` - Displays a list of all category IDs in a server\n・`checkchannel` - Modifies the invite check channel\n・`embed` - A guide on an Embed Creator",inline=False)
            embed.add_field(name="Invites",value="・`check` - Checks invites from provided category",inline=False)
            embed.add_field(name="Utility",value=f"・`prefix` - Shows you the bot's current prefix\n・`guide` - A guide to {client.user.name}\n・`help` - Displays all available commands\n・`ping` - Checks server latency\n・`stats` - Displays bot information",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "ignore":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Admin",inline=False)
            embed.add_field(name="Description",value="Modifies the channel blacklist",inline=False)
            embed.add_field(name="Usage",value=f"`{prefix}ignore <add|remove|list> [#channel]`",inline=False)
            embed.add_field(name="Aliases",value=f"`{prefix}ignore`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "bots":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Admin",inline=False)
            embed.add_field(name="Description",value="Modifies the channel whitelist",inline=False)
            embed.add_field(name="Usage",value=f"`{prefix}bots <add|remove|list> [#channel]`",inline=False)
            embed.add_field(name="Aliases",value=f"`{prefix}bots`",inline=False)
            await ctx.send(embed=embed)

        elif cmd == "checkchannel":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Admin",inline=False)
            embed.add_field(name="Description",value="Modifies the invite check channel",inline=False)
            embed.add_field(name="Usage",value=f"`{prefix}checkchannel #channel`",inline=False)
            embed.add_field(name="Aliases",value=f"`{prefix}checkchannel`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "category":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Admin",inline=False)
            embed.add_field(name="Description",value="Modifies the category whitelist",inline=False)
            embed.add_field(name="Usage",value=f"`{prefix}category <add|remove|list> [categoryChannel]`",inline=False)
            embed.add_field(name="Aliases",value=f"`{prefix}category`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "ids":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Admin",inline=False)
            embed.add_field(name="Description",value="Displays a list of all category IDs in a server",inline=False)
            embed.add_field(name="Usage",value=f"`{prefix}ids`",inline=False)
            embed.add_field(name="Aliases",value=f"`{prefix}ids`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "check":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="General",inline=False)
            embed.add_field(name="Description",value="Checks invites from provided categories. Would check for codeblock errors in the channel by default. ",inline=False)
            embed.add_field(name="Usage",value=f"`{prefix}check`",inline=False)
            embed.add_field(name="Aliases",value=f"`{prefix}check`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "guide":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Utility",inline=False)
            embed.add_field(name="Description",value=f"A guide to {client.user.name}",inline=False)
            embed.add_field(name="Usage",value=f"`{prefix}guide`",inline=False)
            embed.add_field(name="Aliases",value=f"`{prefix}guide`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "help":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Utility",inline=False)
            embed.add_field(name="Description",value="Displays all available commands, including information about a specific command. ",inline=False)
            embed.add_field(name="Usage",value=f"`{prefix}help [check]`",inline=False)
            embed.add_field(name="Aliases",value=f"`{prefix}help`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "ping":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Utility",inline=False)
            embed.add_field(name="Description",value="Checks server latency",inline=False)
            embed.add_field(name="Usage",value=f"`{prefix}ping`",inline=False)
            embed.add_field(name="Aliases",value=f"`{prefix}ping`",inline=False)
            await ctx.send(embed=embed)
            
        elif cmd == "stats":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Utility",inline=False)
            embed.add_field(name="Description",value="Displays bot information",inline=False)
            embed.add_field(name="Usage",value=f"`{prefix}stats`",inline=False)
            embed.add_field(name="Aliases",value=f"`{prefix}stats`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "embed":
            embed=discord.Embed(
                title=f"The {cmd} command",
                url="https://robyul.chat/embed-creator",
                description="Use [this website](https://robyul.chat/embed-creator)!",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Admin",inline=False)
            embed.add_field(name="Description",value="A guide on an Embed Creator",inline=False)
            embed.add_field(name="Usage",value=f"Fill in wanted information in the destined boxes, and copy the code part behind ```_embed #channel```. Then {prefix}embed [code].",inline=False)
            embed.add_field(name="Aliases",value=f"`{prefix}embed`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "invid":
            embed = discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa
            )
            embed.add_field(name="Category",value="Owner",inline=False)
            embed.add_field(name="Description",value="Shows you the server id of the invite provided",inline=False)
            embed.add_field(name="Usage",value=f"`{prefix}invid [invite]`",inline=False)
            embed.add_field(name="Aliases",value=f"`{prefix}invid`",inline=False)
            await ctx.send(embed=embed)
        else:
            embed=discord.Embed(
                description=f"**Error**:Topic `{cmd}` not found or doesn't have a help module yet!",
                colour=0xe74d3f,
            )
            await ctx.send(embed=embed)
    else:
        if cmd == None:
            embed=discord.Embed(
                title=f"{client.user.name}'s commands",
                description=f"Here's the list of available commands. For more specific and detailed help for each commands, use `{prefix}help [command]` like `{prefix}help check`.\nBot prefix: `{prefix}`, <@{client.user.id}>\n\nAvailable Commands: 11",
                colour=0xfffafa,
            )
            embed.add_field(name="Admin",value="・`bots` - Modifies the bot channel list\n・`ignore` - Modifies the channel blacklist\n・`category` - Modifies the category whitelist\n・`ids` - Displays a list of all category IDs in a server\n・`checkchannel` - Modifies the invite check channel\n・embed - A guide on an embed creator",inline=False)
            embed.add_field(name="Invites",value="・`check` - Checks invites from provided category",inline=False)
            embed.add_field(name="Utility",value=f"・`prefix` - Shows you the bot's current prefix\n・`guide` - A guide to {client.user.name}\n・`help` - Displays all available commands\n・`ping` - Checks server latency\n・`stats` - Displays bot information",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "embed":
            embed=discord.Embed(
                title=f"The {cmd} command",
                url="https://robyul.chat/embed-creator",
                description="Use [this website](https://robyul.chat/embed-creator)!",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Admin",inline=False)
            embed.add_field(name="Description",value="A guide on an Embed Creator",inline=False)
            embed.add_field(name="Usage",value=f"Fill in wanted information in the destined boxes, and copy the code part behind ```_embed #channel```. Then {prefix}embed [code].",inline=False)
            embed.add_field(name="Aliases",value=f"`{prefix}embed`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "ignore":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Admin",inline=False)
            embed.add_field(name="Description",value="Modifies the channel blacklist",inline=False)
            embed.add_field(name="Usage",value=f"`{prefix}ignore <add|remove|list> [#channel]`",inline=False)
            embed.add_field(name="Aliases",value=f"`{prefix}ignore`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "bots":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Admin",inline=False)
            embed.add_field(name="Description",value="Modifies the channel whitelist",inline=False)
            embed.add_field(name="Usage",value=f"`{prefix}bots <add|remove|list> [#channel]`",inline=False)
            embed.add_field(name="Aliases",value=f"`{prefix}bots`",inline=False)
            await ctx.send(embed=embed)

        elif cmd == "checkchannel":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Admin",inline=False)
            embed.add_field(name="Description",value="Modifies the invite check channel",inline=False)
            embed.add_field(name="Usage",value=f"`{prefix}checkchannel #channel`",inline=False)
            embed.add_field(name="Aliases",value=f"`{prefix}checkchannel`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "category":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Admin",inline=False)
            embed.add_field(name="Description",value="Modifies the category whitelist",inline=False)
            embed.add_field(name="Usage",value=f"`{prefix}category <add|remove|list> [categoryChannel]`",inline=False)
            embed.add_field(name="Aliases",value=f"`{prefix}category`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "ids":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Admin",inline=False)
            embed.add_field(name="Description",value="Displays a list of all category IDs in a server",inline=False)
            embed.add_field(name="Usage",value=f"`{prefix}ids`",inline=False)
            embed.add_field(name="Aliases",value=f"`{prefix}ids`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "check":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="General",inline=False)
            embed.add_field(name="Description",value="Checks invites from provided categories. Would check for codeblock errors in the channel by default. ",inline=False)
            embed.add_field(name="Usage",value=f"`{prefix}check`",inline=False)
            embed.add_field(name="Aliases",value=f"`{prefix}check`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "guide":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Utility",inline=False)
            embed.add_field(name="Description",value=f"A guide to {client.user.name}",inline=False)
            embed.add_field(name="Usage",value=f"`{prefix}guide`",inline=False)
            embed.add_field(name="Aliases",value=f"`{prefix}guide`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "help":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Utility",inline=False)
            embed.add_field(name="Description",value="Displays all available commands, including information about a specific command. ",inline=False)
            embed.add_field(name="Usage",value=f"`{prefix}help`",inline=False)
            embed.add_field(name="Aliases",value=f"`{prefix}help`",inline=False)
            await ctx.send(embed=embed)
        elif cmd == "ping":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Utility",inline=False)
            embed.add_field(name="Description",value="Checks server latency",inline=False)
            embed.add_field(name="Usage",value=f"`{prefix}ping`",inline=False)
            embed.add_field(name="Aliases",value=f"`{prefix}ping`",inline=False)
            await ctx.send(embed=embed)
            
        elif cmd == "stats":
            embed=discord.Embed(
                title=f"The {cmd} command",
                colour=0xfffafa,
            )
            embed.add_field(name="Category",value="Utility",inline=False)
            embed.add_field(name="Description",value="Displays bot information",inline=False)
            embed.add_field(name="Usage",value=f"`{prefix}stats`",inline=False)
            embed.add_field(name="Aliases",value=f"`{prefix}stats`",inline=False)
            await ctx.send(embed=embed)
        else:
            embed=discord.Embed(
                description=f"**Error**:Topic `{cmd}` not found or doesn't have a help module yet!",
                colour=0xe74d3f,
            )
            await ctx.send(embed=embed)

@client.command()
async def owner(ctx):
    owners = config()["owners"]
    prefix = config()["prefix"] #{prefix}
    f1=f"The main point to why {client.user.name} has to add servers is to limit the amount of servers using it and to reduce the risk of hitting ratelimit."
    f2=f"Use this account to run `{prefix}server add [serverId]` to add a server so the bot will listen to the commands in the servers you added only. If you don't add in a server and invite it, the bot will not listen to any commands, even if you're an admin."
    f3=f"Get the server's ID using the `{prefix}invid [invite]` to get the server ID of the server invite."
    f4=f"You can remove servers that are allowed to use the bot using `{prefix}server remove [serverID]` and list out the servers that are allowed to use the bot using `{prefix}server list`. If there is a value which states `None (serverid)`, the bot is not in the server as of that time."
    f5=f"You can use `{prefix}guilds` to see the total number of servers the bot is in. Note that this is not the list of servers *allowed* to use the bot, it is just merely a list showing which servers the bot is in. If some servers did not appear in the list when you ran `{prefix}server list`, the bot will not listen to any commands in the servers."
    if str(ctx.author.id) in owners:
        embed=discord.Embed(
            title="Welcome to the Bot Owner Guide!",
            description=f"This is the basic guide on how to handle the bot and how to invite it to your portals and other informations. Let's get into it!",
            colour=0xfffafa
        )
        embed.add_field(name="Reasons for server adding",value=f1,inline=False)
        embed.add_field(name="Adding Servers",value=f2,inline=False)
        embed.add_field(name="Server Id with Invite",value=f3,inline=False)
        embed.add_field(name="Removing & Listing Servers",value=f4,inline=False)
        embed.add_field(name="The Bot's Servers",value=f5,inline=False)
        embed.add_field(name=f"Start using {client.user.name}!",value=f"Once you've added in the servers, you can use the bot with all commands in the servers that you've added! You're free to use the bot now. Thank you so much for using the bot! - Uma#2433",inline=False)
        await ctx.send(embed=embed)
    else:
        return

@client.command()
async def guide(ctx):
    prefix = config()["prefix"]
    f1=f'1. By default, {client.user.name} has administrator permissions on its "{client.user.name}" role.'
    f2=f'・To start (if needed), please have an administrator whitelist channels using the `{prefix}bots add <channel>` commands.\n・This is to desinate channels to let users run non-admin commands such as `{prefix}help` and `{prefix}stats`.\n・Administrators can run commands anywhere on the server; however, everyone else can only run commands in __whitelisted__ channels.\n・Please note that both the `{prefix}embed` and `{prefix}check` commands can __only__ be run by administrators.'
    f3=f'1. Set an invite check channel with `{prefix}checkchannel [textChannel]`.\n2. Add the category IDs **(one at a time)** to check invites for using `{prefix}category add [categoryChannelId]`.\n3. Run `{prefix}ids` to see available categories in your portal. \n4. If you have channels that you want to ignore during the invite checks, you can blacklist them using `{prefix}ignore add [#channel]`\n5. Run `{prefix}check` **(in the invite check channel)** and wait a little bit.\n6. __Invite check complete!__'
    f4=f'・For some commands, there are three actions - add, remove, and list:\n・**add** - adds the given channel to the list\n・**remove** - removes the given channel from the list\n・**list** - lists the current channels saved in the list\n・The help command is `{prefix}help`\n・For issues, message Uma#2433'
    embed=discord.Embed(
        title=f"A guide to {client.user.name}",
        colour=0xfffafa,
    )
    embed.add_field(name="Things to know before you start",value=f1,inline=False)
    embed.add_field(name="Setup",value=f2,inline=False)
    embed.add_field(name="Invite checks",value=f3,inline=False)
    embed.add_field(name="Useful stuff",value=f4,inline=False)
    await ctx.send(embed=embed)
            
keep_alive.keep_alive()        
client.run(token)
