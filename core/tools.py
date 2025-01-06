from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from duckduckgo_search import DDGS


TavilySearch = TavilySearchResults(max_results=5)


@tool
def VideoSearch(
    query: str,
    region="wt-wt",
    safesearch="off",
    timelimit="m",
    resolution="high",
    duration="long",
    max_results=5
) -> str:
    """Use this to get videos."""

    try:
        results = DDGS().videos(
            keywords=query,
            region=region,
            safesearch=safesearch,
            timelimit=timelimit,
            resolution=resolution,
            duration=duration,
            max_results=max_results
        )
        videos = [i["embed_url"] for i in results]

        return str(videos)
    except Exception as e:
        return ""


@tool
def ImageSearch(query: str, max_results=5) -> str:
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
