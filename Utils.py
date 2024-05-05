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


class Utils:
    links: list[str]
    search_terms: str
    start: float
    desc: str

    def __init__(self, links: list[str], search_terms: str, start: float):
        self.links = links
        self.search_terms = search_terms
        self.start = start
        self.desc = ""

    async def get_new_embed(self, append: str, new_line: bool = True) -> interactions.Embed:
        self.desc += f"{'\n\n' if new_line else ''}[{((time.perf_counter() * 1000) - self.start):.2f}ms] {append}"
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
                        f"\nTitles:\n```yaml\n{title_msg + " "}\n```\nStatus:\n```yaml\n{self.desc}\n```",
            color=Color(AURORA[color_index % len(AURORA)])
        )
        print(color_index % len(AURORA))
        return embed
