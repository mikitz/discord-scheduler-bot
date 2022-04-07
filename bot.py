# ------------------------
#   Initialize & Imports
# ------------------------
from unicodedata import name
import discord # Import Discord
from discord.ext import commands # Import commands for the bot
bot = commands.Bot(command_prefix='!sb ') # Initialize Bot Commands
bot.remove_command('help')
# ------------------------
#   Bot Command Fuctions
# ------------------------

# Help Command
@bot.command()
async def help(ctx): #!sb help
    embed = discord.Embed(
        tite='Schedule Bot',
        description='Welcome to the help section of Scheduler Bot. See below for a list of commands and their description.',
        color=discord.Colour.green()
    )
    embed.add_field(
        name='Help',
        value="`!sb help` provides a list of all commands.",
        inline=False
    )
    embed.add_field(
        name='Info',
        value="`!sb info` provides information about where the bot's open source code is stored and how to donate to the author.",
        inline=False
    )
    embed.add_field(
        name='Create a New Event',
        value='`!sb event` creates a new event.',
        inline=False
    )
    await ctx.send(embed=embed)

# Info Command
@bot.command()
async def info(ctx): # !sb info
    embed = discord.Embed(
        tite='Schedule Bot',
        description='Schedule Bot Info',
        color=discord.Colour.green()
    )
    embed.set_thumbnail(url='https://avatars.githubusercontent.com/u/17684097?s=400&u=badb2a3839ce5cb4e5c3f75dc3172c1f2786412b&v=4')
    embed.add_field(
        name='Ko-fi',
        value='Buy Mikitz some avocadoes: https://ko-fi.com/mikitz',
        inline=False
    )
    embed.add_field(
        name='GitHub',
        value='View the open-source code: https://github.com/mikitz/discord-scheduler-bot',
        inline=False
    )
    await ctx.send(embed=embed)

# New Event Command
@bot.command()
async def new_event(ctx, name, date, time): # !sb new_event
    await ctx.send(f'New Event -{name}- Starting on {date} at {time}')
# -----------------
#   Start the Bot
# -----------------
bot.run('OTYxMjI1Mzg3MjY5MDI5OTI4.Yk145w.1i-ThKd63JTtBIpKCt8QDiCSLgM') # Start the bot