import discord # Import Discord
from discord.ext import commands # Import commands for the bot

client = discord.Client() # Initialize and Instatiaatae a client object from Discord
# --------------------------
#  When The Bot Goes Online
# --------------------------
@client.event
async def on_ready():
    print("Schedule Bot is online.")
# ---------------------------
#  When User Sends a Message
# ---------------------------
@client.event
async def on_message(message):
    print("Message:", message)
    if message.author == client.user: # Prevent the bot from responding to its own messages
        return
    if message.content == '!schedule new event':
        await message.channel.send("When will it take place?")
    if 'cool' in message.content:
        await message.add_reaction('\U0001F60E')
# ---------------------------
#  When User Edits a Message
# ---------------------------
@client.event
async def on_message_edit(before, after):
    await before.channel.send(
        f'{before.author} edit a message.\n'
        f'Before: {before.content}\n'
        f'After: {after.content}'
    )
# ---------------------------
#  When User Adds a Reaction
# ---------------------------
@client.event
async def on_reaction_add(reaction, user):
    await reaction.message.channel.send(f'{user} reacted with {reaction.emoji}!')
# -----------------------
#      Start the Bot
# -----------------------
client.run('OTYxMjI1Mzg3MjY5MDI5OTI4.Yk145w.1i-ThKd63JTtBIpKCt8QDiCSLgM') # Start the bot