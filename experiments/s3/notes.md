dataset:
- https://www.youtube.com/@PhroxzonLeagueFundamentals

https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors-buckets.html?icmpid=docs_amazons3_console
https://us-east-1.console.aws.amazon.com/dynamodbv2/home?region=us-east-1#service

fair use considerations:
- "In computer- and Internet-related works, the transformative characteristic of the later work is often that it provides the public with a benefit not previously available to it, which would otherwise remain unavailable."
- "The use must be productive and must employ the quoted matter in a different manner or for a different purpose from the original. ...If the secondary use adds value to the original—if the quoted matter is used as raw material, transformed in the creation of new information, new aesthetics, new insights and understandings—this is the very type of activity that the fair use doctrine intends to protect for the enrichment of society."
- https://www.lib.umn.edu/services/copyright/use#fourfactors

- I think I'm okay as long as the works are transformative (they change the wording, change the format, and present it in a beginner-friendly manner).
    - Purposes that favor fair use include education, scholarship, research, and news reporting, as well as criticism and commentary more generally.
    - Using a factual work is more likely to be fair use, using a creative work is less likely to be fair use. This is related to the fact that copyright does not protect facts and data.
    - Using a smaller amount of the source work is more likely to be fair use, and using a larger amount is less likely to be fair use. (the response should only quote parts of the document relevant to the question)

- Google Cloud Speech-To-Text API $0.96/hr (Chirp v2)
- Google Gemini 2.5 Flash
- Azure speech-to-text standard transcription: $0.18-1/hr
- OpenAI Transcribe API (gpt-4o-transcribe): $0.36/hr
- Amazon Transcribe $1.44/hr
- I think the best option (cost and performance) is Gemini 2.5 Flash
- I can speed up the audio (https://news.ycombinator.com/item?id=44376989)
- remove any pauses longer than 20ms (https://news.ycombinator.com/item?id=44378345)

- initial test: Input tokens: 3567, output tokens: 1193
- gpt-4o-transcribe is actually pretty good at LoL content:
    - "Syndra Q can be a hard spell to land sometimes, but I would say more often than not, Faker executes his trade correctly in this position, either by moving a little higher and casting E first to land a stun, or just being a little more patient with his Q to see which direction Renekton will juke in first."

- write a good prompt for transforming the original text

presentation: how to hack time (ekko)
- cut dead time then speed up video by 1-4x
- effectively getting N minutes per minute
- 5-minute video transcription
    - 1x Input tokens: 3567, output tokens: 1193 $0.02085
    - 1.5x Input tokens: 2205, output tokens: 1183 $0.01734 (-17%)
    - 2x Input tokens: 1654, output tokens: 1187 $0.01601 (-23%) (note: minor quality loss, about 1% of tokens)