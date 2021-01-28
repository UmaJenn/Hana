import discord, datetime, time
from discord.ext import commands
from datetime import date
import json

def config(filename: str = "config"):
    """ Fetch default config file """
    try:
        with open(f"config.json", encoding='utf8') as data:
            return json.load(data)
    except FileNotFoundError:
        raise FileNotFoundError("JSON file wasn't found")

owners = config()["owners"]

start_time = time.time()
today = date.today()

class Timeup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_text_channel_count(self):
        """Returns the text channel count from all the guilds the bot is connected to."""
        count = 0
        for guild in self.bot.guilds:
            count += len(guild.text_channels)
        return count

    def get_voice_channel_count(self):
        """Returns the voice channel count from all the guilds the bot is connected to."""
        count = 0
        for guild in self.bot.guilds:
            count += len(guild.voice_channels)
        return count

    @commands.command(pass_context=True)
    async def ping(self, ctx):
        ping_in_millis = round((ctx.bot.latency * 1000))
        current_time = time.time()
        difference = int(round(current_time - start_time))
        m, s = divmod(difference, 60)
        h, m = divmod(m, 60)
        text = f'{h:d}h {m:02d}m {s:02d}s'
        embed1 = await ctx.send(embed=discord.Embed(description = "ping? :ping_pong:",colour=0xfffafa))
        clock = round((embed1.created_at-ctx.message.created_at).total_seconds() * 1000)
        hello = f':heart_decoration: **HB:** {str(ping_in_millis)} ms\n:repeat: **RTT:** {str(clock)} ms\n:arrow_up: **UT:** {text}'
        embed2 = discord.Embed(description=hello,color=0xfffafa)

        await embed1.edit(embed=embed2)

    @commands.command(pass_context=True)
    async def stats(self, ctx):
        current_time = time.time()
        difference = int(round(current_time - start_time))
        m, s = divmod(difference, 60)
        h, m = divmod(m, 60)
        d, h = divmod(m, 24)
        d2 = today.strftime("%b %d, %Y")
        #text = f'{h:d}h {m:02d}m {s:02d}s'
        text = f'{d:d}d {h:02d}h {m:02d}m {s:02d}s'
        owner = await self.bot.fetch_user(owners)
        embed=discord.Embed(
            color=0xfffafa,
        )
        embed.set_footer(text = f"{self.bot.user.name} - an APM utility bot・{d2}")
        embed.set_author(name=f"{self.bot.user.name} v1.3.0",icon_url=self.bot.user.avatar_url)
        embed.add_field(name="Owner",value=f"{owner}",inline=False)
        embed.add_field(name="Developer",value="Uma#2433",inline=False)
        embed.add_field(name="Inspiration",value="**Og InvChecker:** Sakura#3774\n**Developer:** Flare#2851",inline=False)
        embed.add_field(name="General Stuff",value=f"**Guilds:** {len(self.bot.guilds)}\n**Channels:** {self.get_text_channel_count()}\n**Members:** {len(self.bot.users)}",inline=False)
        embed.add_field(name="Random Stuff", value=f"**Uptime:** {text}",inline=False)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(timeup(bot))

