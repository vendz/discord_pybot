import discord
from discord.ext import commands, tasks
from random import choice
# from keep_alive import keep_alive
# from dotenv import load_dotenv
import requests
import json
import os
import youtube_dl
import urllib.request
import re

# load_dotenv()
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
    my_embed = discord.Embed(title="current version", description="This bot is currently in pre-release", color=0x00ff00)
    my_embed.add_field(name="version code:", value="v1.0.5-beta-2", inline=False)
    my_embed.add_field(name="initial release:", value="January 2021", inline=False)
    await context.message.channel.send(embed=my_embed)


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


# a command for bot to join voice channel
@client.command(name='join')
async def join(context):
    if not context.message.author.voice:
        await context.message.channel.send("You are not connected to a voice channel")
        return
    else:
        channel = context.message.author.voice.channel
        voice = discord.utils.get(client.voice_clients, guild=context.guild)
        if voice is None:
            await channel.connect()
        else:
            voice_channel = context.message.author.voice
            await context.message.channel.send("bot is already connected to `{0.channel}` channel".format(voice_channel))


# a command for bot to leave voice channel
@client.command(name='leave', pass_context=True)
async def leave(context):
    voice = discord.utils.get(client.voice_clients, guild=context.guild)
    if voice is not None:
        if voice.is_playing():
            voice.stop()
            await context.message.guild.voice_client.disconnect()
        else:
            await context.message.guild.voice_client.disconnect()
    else:
        voice_channel = context.message.author.voice
        await context.message.channel.send("bot is not connected to `{0.channel}` channel".format(voice_channel))


@client.command(name='play')
async def play(context, *, query: str):
    context.voice_client.stop()
    voice = discord.utils.get(client.voice_clients, guild=context.guild)
    if voice is not None:
        if voice.is_connected():
            search_query = query.strip().replace(" ", "+")
            html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + search_query)
            video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
            fetched_url = "https://www.youtube.com/watch?v=" + video_ids[0]
            FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                              'options': '-vn'}
            ydl_opts = {'format': 'bestaudio'}
            vc = context.voice_client
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(fetched_url, download=False)
                url2 = info['formats'][0]['url']
                source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
                await context.message.channel.send("playing " + fetched_url)
                vc.play(source)
    else:
        await context.message.channel.send("not connected to a voice channel")


@client.command(name='pause')
async def pause(context):
    voice = discord.utils.get(client.voice_clients, guild=context.guild)
    if voice is not None:
        if voice.is_playing():
            voice.pause()
        else:
            await context.message.channel.send("no audio playing...")
    else:
        await context.message.channel.send("no audio playing...")


@client.command(name='resume')
async def resume(context):
    voice = discord.utils.get(client.voice_clients, guild=context.guild)
    if voice is not None:
        if voice.is_paused():
            voice.resume()
        else:
            await context.message.channel.send("no music in queue...")
    else:
        await context.message.channel.send("no music in queue...")


@client.command(name='stop')
async def stop(context):
    voice = discord.utils.get(client.voice_clients, guild=context.guild)
    if voice is not None:
        if voice.is_playing():
            voice.stop()
        else:
            await context.message.channel.send("no music playing...")
    else:
        await context.message.channel.send("no music playing...")


# a command to print help
@client.command(name='help')
async def help_dialog(context):
    await context.message.channel.send("`.version` -- to know which version bot is running on\n"
                                       "`.help` -- to show this dialog\n"
                                       "`.inspire` -- to print a random inspiring quote\n"
                                       "`.join` -- for bot to join a voice channel\n"
                                       "`.leave` -- for bot to leave a voice channel\n"
                                       "`.play <your-query>` -- for bot to play a song\n"
                                       "`.pause` -- for bot to pause playing a song\n"
                                       "`.resume` -- for bot to resume previous song\n"
                                       "`.stop` -- for bot to stop playing a song\n"
                                       "`.kick <member>` -- to kick a member\n"
                                       "`.ban <member>` -- to ban a member\n\n"
                                       "`you can also send youtube URL as query to play command`")


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
        await message.author.send(
            "do not send any text messages in `memes-only` channel")  # it sends a DM to user to stop sending text
        # message in memes-only channel.

    # we add this statement when we have '@client.commands' because if we type  a command then both 'on_message' and
    # 'client.commands' will work on it and   we have to prevent that from happening
    await client.process_commands(message)


# keep_alive()
client.run(os.environ("TOKEN"))
