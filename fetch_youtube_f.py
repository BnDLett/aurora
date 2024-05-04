import yt_dlp
import os
from pathlib import Path


def download_audio(link: str, ydl_opts: dict, file_format: str):
    """
    Downloads audio using the YT-DLP library.
    :param file_format: The format to use.
    :param ydl_opts: The yt-dlp config.
    :param link: The link to the audio to be downloaded.
    :return:
    """
    print("Loading audio... this may take a moment.")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        if not link.startswith("https://") and not link.startswith("www."):
            funny_dict = ydl.extract_info(f"ytsearch:{link}", download=False)['entries'][0]['id']
            link = f"https://youtube.com/watch?v={funny_dict}"

        info = ydl.extract_info(link, False)
        info = ydl.prepare_filename(info)

        info = Path(info)
        info = info.with_suffix(f".{file_format}").__format__("")

        if os.path.exists(info):  # This is for caches (if any)
            return info
        ydl.download([link])

    return info


async def fetch(links: list, search_terms: str, video: bool, file_format: str, codec: str) -> list:
    ydl_opts = {
        'writethumbnail': True,
        'format': 'bestaudio/best',
        'quiet': True,
        "paths": {file_format: 'cache', 'webm': 'cache'},
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
    file_list = []

    for link in links:
        file_list.append(download_audio(link, ydl_opts, file_format))

    return file_list
