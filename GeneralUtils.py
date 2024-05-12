import json
import interactions
import yt_dlp
from interactions import Color
import time

color_index = 0
AURORA = [
    "#01efac",
    "#01cbae",
    "#2082a6",
    "#524096",
    "#5f2a84"
]


class FetchMediaUtils:
    links: list[str]
    search_terms: str
    start: float
    desc: str
    downloaded: int

    def __init__(self, links: list[str], search_terms: str, start: float):
        self.links = links
        self.search_terms = search_terms
        self.start = start
        self.desc = ""
        self.downloaded = 0

    async def add_downloaded(self, amount: int = 1) -> None:
        """
        Adds `amount` (default: 1) to self.downloaded().
        :return: None
        """
        self.downloaded += 1

    async def get_new_embed(self, append: str, new_line: bool = True) -> interactions.Embed:
        """
        Retrieves a new embed and appends a status update.
        :param append: The status update to append to the embed.
        :param new_line: Whether to put two new lines at the start of the status update.
        :return: Embed
        """
        self.desc += f"{'\n\n' if new_line else ''}[{((time.monotonic() * 1000) - self.start):.2f}ms] {append}"
        embed = await self.prepare_embed()

        global color_index
        color_index += 1

        return embed

    async def prepare_embed(self) -> interactions.Embed:
        link_msg = ""
        title_msg = ""
        length = len(self.links)
        global color_index
        ydl_opts = {
            'quiet': True,
            'format': 'bestaudio/best',
        }

        ydl = yt_dlp.YoutubeDL(ydl_opts)

        for pos, link in enumerate(self.links):
            link_msg += f"[{pos}] {link} {'\n\n' if pos < (length - 1) else ''}"

            if not link.startswith("https://") and not link.startswith("www."):
                continue

            info = ydl.extract_info(link, False)
            title = info.get('title')
            title_msg += f"[{pos}] {title} {'\n' if pos < (length - 1) else ''}"

        # Sorry for the mindfuck hell of a string.
        embed = interactions.Embed(
            title="Fetch Media",
            description=f"Link(s) used:\n```yaml\n{link_msg}```\nSearch terms:\n```yaml\n{self.search_terms}\n```"
                        f"\nTitles:\n```yaml\n{title_msg + " "}\n```\nFiles downloaded: ```yaml\n"
                        f"[{self.downloaded}/{len(self.links)}]\n```\nStatus:\n```yaml\n{self.desc}\n```",
            color=Color(AURORA[color_index % len(AURORA)])
        )
        print(color_index % len(AURORA))
        return embed


class Configuration:
    """
    Class that handles configuration for the bot. Streamlines configuration access.
    """
    def __init__(self, fi: str):
        """
        A class that streamlines configuration access.
        :param fi: The path to the configuration file.
        """

        self._fi_stream = open(fi)
        self._fi_content = self._fi_stream.read()
        self._fi_json = json.loads(self._fi_content)

        # General
        self.debug: bool = self._fi_json["debug"]

        # Discord specific configurations
        self.discord_token: str = self._fi_json["token"]
        self.discord_debug_token: str = self._fi_json["debug_token"]
        self.discord_scope: str = self._fi_json["debug_scope"]

        # Reddit specific configurations
        self.reddit_client_id: str = self._fi_json["reddit_client_id"]
        self.reddit_client_secret: str = self._fi_json["reddit_client_secret"]
        self.reddit_client_agent: str = self._fi_json["reddit_client_agent"]
