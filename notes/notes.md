year end summary based on year match data

type of player: one trick or jack of all trades?

how unique are you as a player?
rates for roles, build by champ, other stats/items?

should be sharable - maybe a stats card exportable as an image, or link to the website

https://www.reddit.com/r/slatestarcodex/comments/1nsnhqz/what_are_the_most_impressive_abilities_of_current/

I like Spotify Wrapped's idea of a generative video/slideshow

image generation by inserting your face onto a champ

maybe achievements like the "challenges" system where you can compare yourself in rank to other users

audio component - background music, ping sounds for certain moments

### Spotify Wrapped

https://newsroom.spotify.com/2024-12-04/wrapped-user-experience-2024
- strong unified theme and palette
- generative animated slideshow with stats
- 2024 music evolution by month
- you spent X minutes doing Y; you were in the top X% of Y listeners
- mobile-first design
- personalized messages from artists
- sharing integration with TikTok, Instagram to post directly to your stories
- music videos playlist (LoL version: pros hitting clips with your fav champ)

https://newsroom.spotify.com/2024-12-04/make-this-years-spotify-wrapped-even-more-about-you-with-these-ai-experiences/
- AI features: AI DJ, AI Playlist, Spotify Wrapped AI Podcast
- built on NotebookLM; AI Podcast reviews your top songs, artists, genres
- build AI playlists with natural language like "top 5 genres"


## Design
- consider web-first design for the hackathon project since I assume most people will be on web
- what kind of video format or animations fit web better? wide screen
- what kinds of design are used in LoL? emphasis on art, cohesive aesthetics, lore, fantasy
- visual effects
- sound design: gameplay cues, feedback (good or bad), driving emotion
- user interface; visual design principles: present complex info in a simple, intuitive way.
    - audience: what kinds of things do they connect with? (fav champ)
- https://github.com/pipe01/legendary-rune-maker/tree/master/Legendary%20Rune%20Maker/Images
- https://nasaprospect.com/

- LoL minimap UI with stats per lane as you hover over them
- ARAM stats

## Engineering
- https://github.com/marketplace/actions/download-league-of-legends-data-dragon
- English-only to minimize complexity
- https://morph-text-remotion.vercel.app/?/Empty
- https://text-warping.vercel.app/?/Promo
- https://githubunwrapped.com/szge
- https://engineering.atspotify.com/?s=wrapped
- https://engineering.atspotify.com/2020/2/spotify-unwrapped-how-we-brought-you-a-decade-of-data
    - Google Cloud Bigtable data lake for time series data, query by year and month
- https://engineering.atspotify.com/2020/9/spotify-unwrapped-2019-how-we-built-an-in-app-experience-just-for-you
    - Backend: GKE, CEF (C++ lib) with HTML templates, CSS 3.1
- https://engineering.atspotify.com/2024/1/exploring-the-animation-landscape-of-2023-wrapped
    - shows animation design across three years
    - native builds for Android and iOS - allows for injecting localized text, images
    - view and layer transformations, path manipulations, textures (gradients, blurs)
    - Airbnb's JSON-based animation format, Lottie - create files in After Effects, upload to backend
    - shows when to use Lottie vs. native animation
- https://www.reddit.com/r/RedditEng/comments/11dg385/reddit_recap_series_building_the_backend/
    - BigQuery data -> Amazon Aurora Postgres DB; two cols: user_id, and recap data as json
        - only one lookup required; fast
    - in the hackathon app, could just be s3
    - started with mock data with query and types ready