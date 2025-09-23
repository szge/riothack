from mcp.server.fastmcp import FastMCP
import httpx
import json
from bs4 import BeautifulSoup
from enum import Enum, auto
from typing import List, Callable, Any
import asyncio

mcp = FastMCP("LolWikiServer")

try:
    with open("experiments/mcp/champion.json", "r", encoding="utf-8") as file:
        data = json.load(file)
        CHAMPION_NAMES_RAW = [champion_data["name"]
                              for champion_data in data["data"].values()]
except Exception as e:
    print("Error loading champion name data:", e)
    CHAMPION_NAMES_RAW = []

LOL_WIKI_BASE = "https://wiki.leagueoflegends.com/en-us"
USER_AGENT = "CoachAltMCP"
# the amount of recent patch history to consider e.g. for champion pages
NUM_RECENT_PATCHES = 3


class PageType(Enum):
    CHAMPION = auto(),
    RUNE = auto(),
    SUMMONER_SPELL = auto(),
    ITEM = auto(),
    MONSTER = auto(),
    LATEST_PATCH = auto()


async def parse_wiki_page(page_url: str, page_type: PageType = PageType.CHAMPION) -> str | None:
    headers = {
        "User-Agent": USER_AGENT
    }

    def limit_patch_history(soup: BeautifulSoup, num_children: int = NUM_RECENT_PATCHES * 2) -> None:
        """
        Finds the patch history element by style and keeps only the first num_children children.
        Removes the rest.
        """
        patch_history_elem = soup.find(
            "div",
            attrs={
                "style": lambda value: value and
                "overflow:auto" in value and
                "max-height:" in value and
                "var(--league-grey-2)" in value
            }
        )
        if patch_history_elem:
            children = list(patch_history_elem.children)
            for child in children[num_children:]:
                child.extract()

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(page_url, headers=headers, timeout=20.0)
            response.raise_for_status()
            html = response.text
            soup = BeautifulSoup(html, "html.parser")

            content_elem = soup.find(id="content")
            if content_elem:
                soup = content_elem
            # Fallback to full page if content element not found

            # remove random garbage
            for elem in soup.select(".hidden-metadata.navigation-not-searchable"):
                elem.decompose()

            # extra processing and garbage removal based on page type
            match page_type:
                case PageType.CHAMPION:
                    # remove skins info
                    for elem in soup.select(".lazyimg-wrapper"):
                        elem.decompose()

            limit_patch_history(soup)

            main_content = " ".join(soup.stripped_strings)
            return main_content
        except Exception:
            return None


async def execute_tasks_and_combine(
    tasks: List[Callable[[], Any]],
    task_names: List[str] = None,
    separator: str = "\n\n"
) -> str:
    """
    Execute a list of async tasks concurrently and combine their results into a single string.

    Args:
        tasks: List of async functions/coroutines to execute
        task_names: Optional list of names for error reporting (defaults to task index)
        separator: String to join results with (default: "\n\n")

    Returns:
        Combined string result of all tasks
    """
    if task_names is None:
        task_names = [f"Task {i}" for i in range(len(tasks))]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    combined_data = []
    for i, result in enumerate(results):
        task_name = task_names[i] if i < len(task_names) else f"Task {i}"

        if isinstance(result, Exception):
            combined_data.append(f"Error executing {task_name}: {str(result)}")
        elif result is None:
            combined_data.append(
                f"Error fetching data for {task_name}: No data returned")
        else:
            combined_data.append(str(result))

    return separator.join(combined_data)


MAX_CHAMPIONS_PER_CALL = 5


@mcp.tool()
async def get_champion_data(champion_names: List[str] = ["Janna"]) -> str:
    """
    Get the page from the official League of Legends wiki for the given champions as text.
    The number of champions per call should be at most 5.
    This provides an up-to-date overview of abilities, champion playstyle, stats, and recent patch history.
    Info provided: class, range type, HP, armor, etc.
    """
    champion_names = champion_names[:MAX_CHAMPIONS_PER_CALL]

    tasks = [
        parse_wiki_page(f"{LOL_WIKI_BASE}/{champion_name}", PageType.CHAMPION)
        for champion_name in champion_names
    ]

    return await execute_tasks_and_combine(tasks, champion_names)


MAX_RUNES_PER_CALL = 5


@mcp.tool()
async def get_runes_data(runes: List[str] = ["Dark Harvest"]) -> str:
    """
    Get the page from the official League of Legends wiki for the given runes as text.
    The number of runes per call should be at most 5.
    This provides an up-to-date overview of rune stats and what it does.
    Runes are enhancements that add new abilities or buffs to the champion.
    The player can choose their loadout of runes before the match begins, during champion select, or their Collection tab.
    """
    runes = runes[:MAX_RUNES_PER_CALL]
    tasks = [
        parse_wiki_page(f"{LOL_WIKI_BASE}/{rune}", PageType.RUNE)
        for rune in runes
    ]
    return await execute_tasks_and_combine(tasks, runes)


MAX_SUMMONER_SPELLS_PER_CALL = 5


@mcp.tool()
async def get_summoner_spell_data(summoner_spells: List[str] = ["Flash"]) -> str:
    """
    Get the page from the official League of Legends wiki for the given summoner spells as text.
    The number of summoner spells per call should be at most 5.
    This provides an up-to-date overview of summoner spell stats and what it does.
    Summoner spells are special abilities that all players can have access to based on the map, in addition to their champion abilities.
    Players choose their two preferred summoner spells during champion select.
    """
    summoner_spells = summoner_spells[:MAX_SUMMONER_SPELLS_PER_CALL]
    tasks = [
        parse_wiki_page(f"{LOL_WIKI_BASE}/{summoner_spell}",
                        PageType.SUMMONER_SPELL)
        for summoner_spell in summoner_spells
    ]
    return await execute_tasks_and_combine(tasks, summoner_spells)


MAX_ITEMS_PER_CALL = 5


@mcp.tool()
async def get_item_data(items: List[str] = ["Boots of Swiftness"]) -> str:
    """
    Get the page from the official League of Legends wiki for the given items as text.
    The number of items per call should be at most 5.
    This provides an up-to-date overview of an item's stats, what it does, and possible how it affects strategy.
    An item is a modular enhancement that grants bonuses and capabilities beyond what champions have access to by default.
    Most items can be purchased from the shop in exchange for An icon representing Gold gold while near the spawn, while a small number of them may be distributed to players from various effects.
    """
    items = items[:MAX_ITEMS_PER_CALL]
    tasks = [
        parse_wiki_page(f"{LOL_WIKI_BASE}/{item}", PageType.ITEM)
        for item in items
    ]
    return await execute_tasks_and_combine(tasks, items)


MAX_MONSTERS_PER_CALL = 5


@mcp.tool()
async def get_monster_data(monster_names: List[str] = ["Blue Sentinel"]) -> str:
    """
    Get the page from the official League of Legends wiki for the given monsters as text.
    The number of monsters per call should be at most 5.
    This provides an up-to-date overview of monster stats, HP, resistances, reward buffs, and possibly how it influences strategy.
    Monsters are neutral units in League of Legends.
    Unlike minions, monsters do not fight for either team, and will only do so if provoked.
    """
    monster_names = monster_names[:MAX_MONSTERS_PER_CALL]
    tasks = [
        parse_wiki_page(f"{LOL_WIKI_BASE}/{monster_name}", PageType.MONSTER)
        for monster_name in monster_names
    ]
    return await execute_tasks_and_combine(tasks, monster_names)


# TODO: implement this
# @mcp.tool()
# async def get_latest_patch_data() -> str:
#     return ""


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
