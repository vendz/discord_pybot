import discord
from discord.utils import find
from discord.ext import commands, tasks
from random import choice
import requests
import json
import os
import youtube_dl

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
    my_embed = discord.Embed(title="current version", description="this is bot is in version 1.2.1", color=0x00ff00)
    my_embed.add_field(name="version code:", value="v1.2.1", inline=False)
    my_embed.add_field(name="initial release:", value="January 2021", inline=False)
    await context.message.channel.send(embed=my_embed)


# a command to kick a member
@client.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick(context, member: discord.Member):
    await member.kick()
    await context.send(member.display_name + " has been kicked! 🚫")


# a command to ban a member
@client.command(name='ban')
@commands.has_permissions(kick_members=True)
async def ban(context, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await context.send(member.display_name + " has been Banned! 🚫")


# a command to print random quote
@client.command(name='inspire')
async def inspire(context):
    quote = get_quote()
    await context.message.channel.send(quote)


# a command for bot to join voice channel
@client.command(name='join')
async def join(context):
    if not context.message.author.voice:
        await context.message.channel.send("You are not connected to a voice channel ❌")
        return
    else:
        channel = context.message.author.voice.channel
        voice = discord.utils.get(client.voice_clients, guild=context.guild)
        if voice is None:
            await channel.connect()
            await context.message.channel.send(f"👍 **Joined** `{context.message.author.voice.channel}` 📄 **And bound to** `{context.message.channel}`")
        else:
            voice_channel = context.message.author.voice
            await context.message.channel.send("bot is already connected to `{0.channel}` channel :warning:".format(voice_channel))


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
        await context.message.channel.send("bot is not connected to `{0.channel}` channel ❌".format(voice_channel))


@client.command(name='play')
async def play(context, *, query: str):
    voice = discord.utils.get(client.voice_clients, guild=context.guild)
    if voice is not None:
        context.voice_client.stop()
        if voice.is_connected():
            await play_func(context, query, voice)
    else:
        channel = context.message.author.voice.channel
        await channel.connect()
        await context.message.channel.send(f"👍 **Joined** `{context.message.author.voice.channel}` 📄 **And bound to** `{context.message.channel}`")
        await play_func(context, query, voice)


@client.command(name='pause')
async def pause(context):
    voice = discord.utils.get(client.voice_clients, guild=context.guild)
    if voice is not None:
        if voice.is_playing():
            voice.pause()
            await context.message.channel.send("**Paused ⏸**")
        else:
            await context.message.channel.send("no audio playing... ❌")
    else:
        await context.message.channel.send("no audio playing... ❌")


@client.command(name='resume')
async def resume(context):
    voice = discord.utils.get(client.voice_clients, guild=context.guild)
    if voice is not None:
        if voice.is_paused():
            voice.resume()
            await context.message.channel.send("**Resumed :arrow_forward:**")
        else:
            await context.message.channel.send("no music was playing... ❌")
    else:
        await context.message.channel.send("no music was playing.. ❌")


@client.command(name='stop')
async def stop(context):
    voice = discord.utils.get(client.voice_clients, guild=context.guild)
    if voice is not None:
        if voice.is_playing():
            voice.stop()
            await context.message.channel.send("**Stopped 🛑**")
        else:
            await context.message.channel.send("no music playing... ❌")
    else:
        await context.message.channel.send("no music playing... ❌")


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


@client.event
async def on_guild_join(guild):
    general = find(lambda x: x.name == 'general',  guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send("**Thanks for adding Vendz**\n\n"
        "`-` My prefix is `.`\n"
        "`-` Use `.help` to view all my commands\n"
        "`-` Currently I can only play from YouTube")


def convertToMinutes(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    if hour != 0:
        return "%d:%02d:%02d" % (hour, minutes, seconds)
    elif hour == 0:
        return "%02d:%02d" % (minutes, seconds)


async def play_func(context, query, voice):
    await context.message.channel.send("**Searching** :mag_right: `" + query + "`")
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                        'options': '-vn'}
    ydl_opts = {'format': 'bestaudio'}
    vc = context.voice_client
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
        audio_url = info['formats'][0]['url']
        title = info['title']
        channel = info['channel']
        thumbnail = info['thumbnails'][1]['url']
        duration = convertToMinutes(info['duration'])
        source = await discord.FFmpegOpusAudio.from_probe(audio_url, **FFMPEG_OPTIONS)
        my_embed = discord.Embed(title="**" + title + "**", url=info['webpage_url'], color=discord.Color.red())
        my_embed.set_author(name="Now Playing...🎶", icon_url=context.author.avatar_url)
        my_embed.set_thumbnail(url=thumbnail)
        my_embed.add_field(name="Channel", value=channel, inline=True)
        my_embed.add_field(name="Duration", value=duration, inline=True)
        await context.message.channel.send(embed=my_embed)
        vc.play(source)


client.run(os.environ["TOKEN"])
