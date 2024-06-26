import asyncio
import threading
import time
import random
from pprint import pprint

import aiohttp
import asyncpraw
import asyncprawcore.exceptions
import interactions
import yt_dlp
from interactions import slash_command, SlashContext, slash_option, OptionType, SlashCommandChoice, check, is_owner

import GeneralUtils
from GeneralUtils import FetchMediaUtils, Configuration

# Command imports
import fetch_youtube_f
from reddit_commands import fetch_post, fetch_profile

FORMATS: list[list[str]] = [
    ['ogg', 'vorbis'],
    ['opus', 'opus'],
    ['mp3', 'mp3'],
    # ['mp4', 'h264']
]
FORMAT_CHOICES = []
for index, fi_format in enumerate(FORMATS):
    FORMAT_CHOICES.append(SlashCommandChoice(fi_format[0], index))
VERSION = "2.3.0a"

# Globals
color_index = 0
bot = interactions.AutoShardedClient()
config = Configuration("conf.json")

if config.debug:
    bot.debug_scope = config.discord_scope
    token = config.discord_debug_token
else:
    token = config.discord_token

bot.load_extension("interactions.ext.jurigged")


# Commands
@interactions.listen()
async def on_startup():
    print(f"Bot is ready!\nCurrently in {len(bot.guilds)} servers.")


@slash_command(
    name="ping",
    description="Checks the latency of the bot.",
)
async def ping(ctx: SlashContext):
    embed = interactions.Embed(
        title="Pong!",
        description=f"```yaml\n{(bot.latency * 1000):.2f}ms\n```"
    )
    await ctx.send(embed=embed)


@slash_command(
    name="update_commands",
    description="Updates the bots commands. Removes old ones, adds new ones.",
)
async def update_commands(ctx: SlashContext):
    ctx.bot.interaction_tree.update()
    await ctx.send("Updated!")


@slash_command(
    name="fetch_media",
    description="Fetches an audio/video file from a supported website.",
)
@slash_option(
    name="links",
    description="The links to use.",
    opt_type=OptionType.STRING
)
@slash_option(
    name="search_terms",
    description="The search terms to use.",
    opt_type=OptionType.STRING
)
@slash_option(
    name="video",
    description="Whether or not to upload a video file or an audio file.",
    opt_type=OptionType.BOOLEAN
)
@slash_option(
    name="file_format",
    description="The format of the file.",
    opt_type=OptionType.NUMBER,
    choices=FORMAT_CHOICES
)
async def fetch_media(ctx: SlashContext, file_format: int = 0, links: str = "", search_terms: str = "None",
                      video: bool = False):
    start = time.monotonic() * 1000

    utils = FetchMediaUtils(["Links are not yet ready."], search_terms, start)
    embed = await utils.get_new_embed("Fiddling with variables...", new_line=False)
    msg = await ctx.send(embed=embed)

    file_format_list: list[str] = FORMATS[int(file_format)]  # For some reason, INTEGER option returns float and not int
    file_format = file_format_list[0]
    codec = file_format_list[1]
    links: list[str] = links.split(", ")
    utils.links = links

    embed = await utils.get_new_embed("Variable fiddling done, downloading file(s) now.")
    await msg.edit(embed=embed)

    if search_terms == "None":
        search_terms = ""
    file_list = await fetch_youtube_f.fetch(links, search_terms, video, file_format, codec, msg, utils)

    embed = await utils.get_new_embed("File(s) are now downloaded and/or were previously cached, proceeding with "
                                      "upload process.")
    await msg.edit(files=file_list, embed=embed)


@slash_command(
    name="optimized_media_fetch",
    description="An optimized version of the `fetch_media` command that comes at the cost of some QOL features.",
)
@slash_option(
    name="link_string",
    description="The links to use.",
    opt_type=OptionType.STRING
)
@slash_option(
    name="file_format",
    description="The format of the file.",
    opt_type=OptionType.NUMBER,
    choices=FORMAT_CHOICES
)
async def optimized_media_fetch(ctx: SlashContext, file_format: int = 0, link_string: str = "", search_terms: str = "None",
                                video: bool = False):
    await ctx.send("Processing your request. This may take a moment.")
    start = time.time()

    channel = ctx.channel
    links = link_string.split(', ')
    filepaths = []

    file_format_list: list[str] = FORMATS[int(file_format)]
    file_format = file_format_list[0]
    codec = file_format_list[1]

    ydl_opts = {
        'writethumbnail': True,
        'format': 'bestaudio/best',
        'quiet': True,
        'ignore-errors': True,
        "paths": {file_format: 'cache', 'webm': 'cache'},
        'outtmpl': "cache/%(title)s-%(id)s.%(ext)s",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': codec,
            'preferredquality': '192'
        }, {
            'key': 'FFmpegMetadata',
            'add_metadata': True
        },
            {
                'key': 'EmbedThumbnail',
                'already_have_thumbnail': False,
            }
        ], }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        if config.debug:
            await channel.send(f'[DEBUG] [{time.time() - start}] Starting download now.')

        for link in links:
            link_info = ydl.extract_info(link)
            filepath = link_info['requested_downloads'][0]['filepath']
            filepaths.append(filepath)

    if config.debug:
        await channel.send(f'[DEBUG] [{time.time() - start}] Starting upload now.')

    # asyncio.run(channel.send("Success!"))
    await channel.send(
        content="",
        files=filepaths
    )
    await channel.send(f"Request finished in `{time.time() - start}` seconds.")


@slash_command(
    name="fetch_subreddit_post",
    description="Fetches a post from a subreddit.",
)
@slash_option(
    name="subreddit",
    description="The subreddit to fetch a post from.",
    opt_type=OptionType.STRING,
    required=True
)
@slash_option(
    name="nsfw_allowed",
    description="If a NSFW post is allowed or not. Could increase the time it takes to fetch a post.",
    opt_type=OptionType.BOOLEAN,
    required=False
)
async def fetch_subreddit_post(ctx: interactions.SlashContext, subreddit: str, nsfw_allowed: bool = False):
    await ctx.send("Fetching post. This may be a moment.", ephemeral=True)
    attempts = 0
    returned: asyncpraw.reddit.Submission

    async with asyncpraw.Reddit(
            client_id=config.reddit_client_id,
            client_secret=config.reddit_client_secret,
            user_agent=config.reddit_client_agent
    ) as reddit:
        returned: tuple = await fetch_post(subreddit, reddit)
        is_nsfw = returned[2]

        while is_nsfw and not nsfw_allowed and attempts < 4:
            returned: tuple = await fetch_post(subreddit, reddit)
            is_nsfw = returned[2]
            attempts += 1

    if is_nsfw and not nsfw_allowed:
        await ctx.send("Could not find a post that was not NSFW. Try again, choose a different subreddit, or allow "
                       "NSFW.")
        return

    ephemeral_enabled = is_nsfw and not ctx.channel.nsfw

    await ctx.send(
        embed=returned[0],
        ephemeral=ephemeral_enabled
    )


@slash_command(
    name="fetch_redditor",
    description="Fetches a redditor by username.",
)
@slash_option(
    name="username",
    description="The username of the redditor.",
    opt_type=OptionType.STRING,
    required=True
)
async def fetch_redditor(ctx: interactions.SlashContext, username: str):
    msg = await ctx.send("Fetching Redditor. This may be a moment.")

    async with asyncpraw.Reddit(
            client_id=config.reddit_client_id,
            client_secret=config.reddit_client_secret,
            user_agent=config.reddit_client_agent
    ) as reddit:
        try:
            embed = await fetch_profile(username, reddit)
            embed.color = "#FF4500"  # Too lazy to natively implement it into the original function.
        except asyncprawcore.exceptions.NotFound:
            embed = interactions.Embed(
                title="User Not Found",
                description="The user you were looking for could not be found. Please ensure that the username is "
                            "correct.",
                color=interactions.Color("#f0790a")
            )

    await msg.edit(content="", embed=embed)


@slash_command(
    name="bot_statistics",
    description="Fetch bot statistics.",
)
async def bot_statistics(ctx: interactions.SlashContext):
    color = random.choice(GeneralUtils.AURORA)

    embed = interactions.Embed(
        title="Bot Statistics",
        description=f"Servers: `{len(bot.guilds)}`\nVersion: `{VERSION}`",
        color=color
    )

    await ctx.send(embed=embed)


@slash_command(
    name="servers",
    description="The servers that the bot is in.",
)
@check(is_owner())
async def servers(ctx: interactions.SlashContext):
    string = ""
    server: interactions.Guild
    color = random.choice(GeneralUtils.AURORA)

    for server_index, server in enumerate(bot.guilds):
        escape = "\n" if not (server_index + 1) == len(bot.guilds) else ""
        string += f"[{server_index + 1}]: {server.name} {escape}"

    embed = interactions.Embed(
        title="Servers",
        description=f"```yaml\n{string}\n```",
        color=color
    )

    await ctx.send(embed=embed)


bot.start(token)
