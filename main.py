import discord
from discord.ext import commands, tasks
import os
import requests
import json
from random import choice
from keep_alive import keep_alive
from discord import Game
from ctypes.util import find_library
from discord import opus
import nacl

client = commands.Bot(command_prefix='.', help_command=None)

status = ['jamming out to music!', 'Eating!', 'Sleeping!']


# using 'zenquotes' API and defining a function
def get_quote():
    response = requests.get('https://zenquotes.io/api/random')
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + '\n\t-' + json_data[0]['a']

    return quote


# changing Bot's status every 20 seconds
@tasks.loop(seconds=20)
async def change_status():
    await client.change_presence(activity=discord.Game(choice(status)))


# a command to display version of the bot
@client.command(name='version')
async def version(context):
    myEmbed = discord.Embed(title="current version", description="The bot is in version 1.0", color=0x00ff00)
    myEmbed.add_field(name="version code:", value="v1.0.0", inline=False)
    myEmbed.add_field(name="date released:", value="January 2021", inline=False)
    await context.message.channel.send(embed=myEmbed)


# a command to kick a member
@client.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick(context, member: discord.Member):
    await member.kick()
    await context.send(member.display_name + " has been kicked!")


# a command to ban a member
@client.command(name='ban')
@commands.has_permissions(kick_members=True)
async def ban(context, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await context.send(member.display_name + " has been Banned!")


# a command to print random quote
@client.command(name='inspire')
async def inspire(context):
    quote = get_quote()
    await context.message.channel.send(quote)


@client.command(name='join')
async def join(context):
    if not context.message.author.voice:
        await context.message.channel.send("You are not connected to a voice channel")
        return
    else:
        channel = context.message.author.voice.channel
    await channel.connect()


@client.command(name='leave', pass_context=True)
async def leave(context):
    await context.message.guild.voice_client.disconnect()


# a command to print help
@client.command(name='help')
async def help(context):
    await context.message.channel.send("`.version` -- to know which version bot is running on\n"
                                       "`.inspire` -- to print a random inspiring quote\n"
                                       "`.join` -- for bot to join a voice channel\n"
                                       "`.leave` -- for bot to leave a voice channel\n"
                                       "`.play` -- for bot to play a song\n"
                                       "`.stop` -- for bot to stop playing a song\n"
                                       "`.kick <member>` -- to kick a member\n"
                                       "`.ban <member>` -- to ban a member\n\n"
                                       "// No text-messages allowed in meme-only channel\n"
                                       "// type <send me DM> to receive a DM from BOT")


@client.event
# printing bot's name on terminal while running
async def on_ready():
    change_status.start()
    print("we have logged in as {0.user}".format(client))


@client.event
async def on_message(message):
    # ignoring any messages sent by bot itself
    if message.author == client.user:
        return

    # deleting any text from 'memes-only' channel
    if str(message.channel) == 'memes-only' and message.content != "":
        await message.channel.purge(limit=1)

    # sending DM to author of message
    if message.content == 'send a DM':
        await message.author.send("This is a DM! \nHave a good day!")

    # we add this statement when we have '@client.commands' because if we type  a command then both 'on_message' and
    # 'client.commands' will work on it and   we have to prevent that from happening
    await client.process_commands(message)


keep_alive()
client.run(os.getenv('TOKEN'))
