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

Filter:
- needs to use AI centrally
- coaching agent