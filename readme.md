Hackathon Resources:
- [List of resources](https://riftrewind.devpost.com/resources)
- [Workshop schedule](https://docs.google.com/document/d/1d8l462pyoALIbe3JbR5FSkiokv5A5aRGe3Ug08mRloU/edit?tab=t.0)
- [AWS resources](https://docs.google.com/document/d/1zSmIWKUi8w20LrJYE5-mJpzNeJ8LTJKkFpy2iIhrzXk/edit?tab=t.0#heading=h.abbfqc3r78ge)


Goal: build an AI-powered agent to help LoL player reflect, learn, and improve
- Full-Year Match History – use this to identify growth areas, uncover persistent habits, and generate an end-of-year recap experience.

Build tools that enable:
- Insights into persistent strengths and weaknesses
- Visualizations of player progress over time
- Fun, shareable year-end summaries (e.g., most-played champions, biggest improvements, highlight matches)
- Social comparisons (e.g., how you stack up against friends or which playstyles complement yours)
- Socially shareable moments and insights — creative ways for players to engage with friends on social platforms using their data

Ideas:
- chat interface with embedded interactive, dynamic, generative UI for users to chat about their gameplay and how to improve
- AI context
    - (always included) definitions page for context about what all the LoL-specific terms mean
    - create a database with scraped documents/transcripts from the best/pro players
    - LoL wiki as a data source (maybe implement as a tool call)
- train a machine learning model to estimate someone's rank based on their stats, without peeking at their actual rank (then use PCA or something to determine importance)
- focus on new players
- focus on experienced players
- really specific advice for one-tricks about their champion mechanics
- item and rune builds
- flashcard generator (e.g. given X scenario, group or split?)
- [Interactive GitHub skyline](https://github.com/github/gh-skyline)
- itero.gg: drafting tool, champion pool builder, personality quiz
- recommended champion based on your spotify history (e.g. Varus or Amumu for emo enjoyers)
- [LoL s11-13 gameplay dataset (train AI agent)](https://github.com/MiscellaneousStuff/tlol)
- [LoL OpenCV AI bot](https://github.com/Oleffa/LeagueAI)
- [minigames](https://loldodgegame.com/dodge/)
- [op.gg MCP](https://github.com/opgginc/opgg-mcp)
    - I could create a MCP server(s) for grounded info on items, pro player advice, etc.

Filter:
- needs to use AI centrally
- coaching agent
- helps players learn

Judging criteria:

Insight Quality
- clear, helpful, relevant takeways for avg League player. makes it easy to improve or reflect
Technical Execution
- project runs smoothly and reliably. Well-structured, efficient, and thoughtfully built
Creativity & UX
- Experience polished, intuitive, and fun to use. something players would actually want to engage with
AWS Integration
- AWS tools used in smart, impactful ways that go beyond the basics. project showcases what’s possible with generative AI and Amazon Bedrock?
Unique & Vibes
- project feels fresh, fun, or delightfully unexpected brings something new or memorable to the player experience that stands out from typical stat tools