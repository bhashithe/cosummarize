from newspaper import Article
import cohere
import logging
import ast
import tweepy
from urlextract import URLExtract
import time

with open('.key') as f:
    text = f.read()

keys = ast.literal_eval(text)

logger = logging.getLogger()

def summarize(url):
    article = Article(url)
    article.download()
    article.parse()
    text = article.text

    co = cohere.Client(keys['cohere'])

    response = co.summarize(
        text=text,
        length='medium',
        format='paragraph'
    )
    return response.summary

def create_api():
    consumer_key = keys["consumer_key"]
    consumer_secret = keys["consumer_secret"]
    access_token = keys["access_token"]
    access_token_secret = keys["access_token_secret"]

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)
    try:
        api.verify_credentials()
    except Exception as e:
        logger.error("Error creating API", exc_info=True)
        raise e
    logger.info("API created")
    return api


def check_mentions(api, keywords, since_id):
    logger.info("Retrieving mentions")
    new_since_id = since_id
    for tweet in tweepy.Cursor(api.mentions_timeline, since_id=since_id).items():
        new_since_id = max(tweet.id, new_since_id)
        if tweet.in_reply_to_status_id is not None:
            continue
        url = extract_url(tweet.text)
        logger.info(f"Answering to {tweet.user.name}")
        summary = summarize(url)
        api.update_status(
            status=summary,
            in_reply_to_status_id=tweet.id,
        )
    with open('.lastid', 'w') as f:
        f.write(new_since_id)

def extract_url(text):
    '''
    we shall only summarize first URL for now
    '''
    extractor = URLExtract()
    url = extractor.find_urls(text)
    return url[0]


def main():
    api = create_api()
    with open('.lastid') as f:
        since_id = int(f.read().strip())

    while True:
        check_mentions(api, ["help", "support"], since_id)
        logger.info("Waiting...")
        time.sleep(60)

if __name__ == "__main__":
    main()

    
