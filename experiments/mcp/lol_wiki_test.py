from lol_wiki import get_champion_data, get_runes_data, get_summoner_spell_data, get_monster_data, get_item_data
import asyncio

if __name__ == "__main__":
    # print(asyncio.run(get_champion_data(["Janna", "Aatrox"])))
    # print(asyncio.run(get_summoner_spell_data(["Flash", "Heal"])))
    # print(asyncio.run(get_runes_data(["Legend: Bloodline", "Fleet Footwork"])))
    # print(asyncio.run(get_monster_data(["Blue Sentinel", "Ancient Krug"])))
    print(asyncio.run(get_item_data(["Boots of Swiftness", "Fated Ashes"])))