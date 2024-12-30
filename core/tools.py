from langchain_community.tools.tavily_search import TavilySearchResults

from typing import Literal
from langchain_core.tools import tool

from duckduckgo_search import DDGS


TavilySearch = TavilySearchResults(max_results=5)


@tool
def YoutubeSearch(query: str, max_results=5) -> str:
    """Use this to get youtube videos."""

    query = f"""
        YouTube videos related to the following content:
        \n{query}
    """

    try:
        ddg = DDGS()
        results = ddg.text(query, max_results=max_results)
        yt_videos = [i for i in results
                     if i["href"].startswith("https://www.youtube.com/watch?v=")]
        videos = []
        for yt_video in yt_videos:
            id = yt_video["href"].removeprefix(
                "https://www.youtube.com/watch?v=")
            videos.append(id)

        return str(videos)
    except Exception as e:
        return ""


@tool
def image_search(query: str, max_results=5) -> str:
    """Use this to get images."""

    query = f"""
        Direct URL of image files (JPEG, PNG, SVG, ...) related to the following content:
        \n{query}
    """

    try:
        ddg = DDGS()
        results = ddg.text(query, max_results=max_results)
        print(results[0])
        # yt_videos = [i for i in results
        #              if i["href"].startswith("https://www.youtube.com/watch?v=")]
    except Exception as e:
        return ""


# image_search("What is a heart attack?")
