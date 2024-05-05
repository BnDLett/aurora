import time
import interactions
from interactions import slash_command, SlashContext, slash_option, OptionType, SlashCommandChoice
import json
from Utils import Utils

# Command imports
import fetch_youtube_f

FORMATS: list[list[str]] = [
    ['ogg', 'vorbis'],
    ['opus', 'opus'],
    # ['mp4', 'h264']
]
FORMAT_CHOICES = []
for index, fi_format in enumerate(FORMATS):
    FORMAT_CHOICES.append(SlashCommandChoice(fi_format[0], index))
VERSION = "2.0.0a"

# Globals
color_index = 0

bot = interactions.AutoShardedClient()
with open("conf.json") as conf_json:
    result = json.loads(conf_json.read())

    token: str = result['token']
    scopes: list[int] = result['scopes']


@interactions.listen()
async def on_startup():
    print("Bot is ready!")


@slash_command(
    name="ping",
    description="Checks the latency of the bot.",
    scopes=scopes,
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
    scopes=scopes
)
async def update_commands(ctx: SlashContext):
    ctx.bot.interaction_tree.update()
    await ctx.send("Updated!")


@slash_command(
    name="fetch_media",
    description="Fetches an audio/video file from a supported website.",
    scopes=scopes,
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
    start = time.perf_counter() * 1000

    utils = Utils(["Links are not yet ready."], search_terms, start)
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


bot.start(token)
