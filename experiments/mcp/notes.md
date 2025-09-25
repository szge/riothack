Coach Alt
(this could be seen as an "alternative tutorial" for LoL)

goal: build an AI agent chatbot focused on improving fundamentals for beginner and intermediate players.
input:
- users supply their summoner id and region
- users can possibly choose from different "modes" for the chat to focus on
    - noob, beginner, intermediate.
    - runes, item builds

engineering:
- build an MCP server (similar to OP.GG) that supplies missing but crucial information
- need to build a database of sound fundamental advice for what new players should focus on
- `uv run mcp install server.py`
- the function docstrings actually matter since they're fed to the agent.
- it appears that MCP doesn't like f-strings for docstrings and the agent doesn't read them properly.

features:
- supplies sound fundamental advice for improving
    - focus on one skill at a time, have fun while playing the game, play in blocks of 3
    - try out different roles and classes, then pick your favourite role and champion to master
- maybe have minigames associated with the knowledge aspects of the game
    - flash cards for champs and their basic abilities without going into too much stat detail
    - show a critical position and ask for thought process on what to do in this scenario
- AI context
    - (always included) definitions page for context about what all the LoL-specific terms mean
    - create a database with scraped documents/transcripts from the best/pro players
        - annotated with tags? for easy lookup by skill, e.g. macro, micro, jungle pathing, etc.
    - LoL wiki as a data source / MCP server
        - champions, runes, summoner spells, items, main monsters, latest patch
    - op.gg MCP server
        - detailed matchup runes, builds, winrates
        - their items page is kinda ass due to bloat. maybe write my own

dataset:
- what's missing from the op.gg MCP server?
    - macro, decision-making


resources:
- [op.gg chatbot](https://help.op.gg/hc/en-us/articles/50542735364761-OP-GG-AI-Chatbot-usage-guide)
- https://meeko.ai/ I like their components and design

other notes:
- item and rune builds
- flashcard generator (e.g. given X scenario, group or split?)
- focus on new players
- focus on experienced players
- it's probably much easier to build an agent that supports beginner or intermediate players.
    - assuming their fundamentals are sound, master+ players probably require fine-grained VOD analysis for meaningful results. the quality of the advice needs to be much higher.
- chat interface with embedded interactive, dynamic, generative UI for users to chat about their gameplay and how to improve
- start with something like a text-based chatbot, then add images and generative UI later
- maybe this doesn't even need to be a standard chatbot interface. it would be much cooler to have the minigames be integrated into a canvas seamlessly into the chat. maybe like https://www.anthropic.com/news/build-artifacts

why a chatbot?
a chatbot can provide flexibility and use unstructured information, meaning datasets are easy to create.

what problem are we trying to solve?
LoL has a steep learning curve for beginners, and they often don't know what to focus on, and where to find high-quality resources.


TODO:
- [x] allow N parallel wiki page calls to the same tool; e.g. allow `List[str]` as input to `get_summoner_spell_data()`
- [x] patch history should be restricted to the N most recent patches; filter out before parsing bs4 text
- [x] fix champ names or use Levenshtein etc
- [x] if a tool call fails, return the list of valid inputs from the Riot API (e.g. champ names)
- Claude's `uv` uses the global `uv` installed on my system, instead of the `uv` for this project. annoying

presentation:
- a central problem for AI agents is hallucation.
    - "every LLM output is hallucination. but some are useful hallucinations"
- we fix this by grounding the outputs as much as possible with high-quality, up-to-date, and concise data that can be fetched quickly
- op.gg MCP is okay, but has a lot of missing stuff. for example, looking up BORK's item metadata only gives you build path but not passive effects, active ability
- LoL wiki as a data source; the pages themselves are huge, so we need to cut down on the size. we do this by removing unnecessary elements by page category. beautiful soup for parsing HTML and extracting only text (we don't need the HTML tags)
    - example: Aatrox page went from 10002 -> 3053 words, speeding up later agent text generation and saving on costs