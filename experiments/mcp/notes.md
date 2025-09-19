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
    - LoL wiki as a data source (maybe implement as a tool call)
    - op.gg MCP server

resources:
- [op.gg chatbot](https://help.op.gg/hc/en-us/articles/50542735364761-OP-GG-AI-Chatbot-usage-guide)

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