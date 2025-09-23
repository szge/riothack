from mcp.server.fastmcp import FastMCP
import httpx
import json
from bs4 import BeautifulSoup

mcp = FastMCP("LolWikiServer")

try:
    with open("experiments/mcp/champion.json", "r", encoding="utf-8") as file:
        data = json.load(file)
        CHAMPION_NAMES_RAW = [champion_data["name"] for champion_data in data["data"].values()]
        # print(CHAMPION_NAMES_RAW)
except Exception as e:
    print("Error loading champion name data:", e)
    CHAMPION_NAMES_RAW = []

LOL_WIKI_BASE = "https://wiki.leagueoflegends.com/en-us"
USER_AGENT = "CoachAltMCP"


async def parse_wiki_page(page_url: str) -> str | None:
    headers = {
        "User-Agent": USER_AGENT
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(page_url, headers=headers, timeout=20.0)
            response.raise_for_status()
            html = response.text
            soup = BeautifulSoup(html, "html.parser")

            # remove this random garbage
            for elem in soup.select(".hidden-metadata.navigation-not-searchable"):
                elem.decompose()

            main_content = " ".join(soup.stripped_strings)
            return main_content
        except Exception:
            return None


@mcp.tool()
async def get_champion_data(champion_name: str) -> str:
    """Get the page from LoL wiki for a given champion"""
    page_data = await parse_wiki_page(f"{LOL_WIKI_BASE}/{champion_name}")
    return "Unable to fetch page data" if page_data == "" else page_data


if __name__ == "__main__":
    mcp.run(transport="streamable-http")