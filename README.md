# Cohere Summarize

This is an experimental application to summarize web-articles using Cohere/summarize endpoint. The app will run as a Twitter bot where users can reply in a tweet with a URL in it and the bot will extract the URL and then act on the text content of the website.

## TODO
- We have not decided on how to handle websites which are not text.
    - Ultimately websites with videos/audios should be converted to text in-order to be summarized
    - Find a free or opensource model to extract text from audio
- Twitter bots read/write permission issue.
- Add functionality such following to the bot
    - Bullet points
    - Larger summary