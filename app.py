from bs4 import BeautifulSoup
from newspaper import Article
import cohere
import logging
import ast
from mastodon import Mastodon
import time
import sqlite3

'''
TODO: Create a database of replied posts so that we do not repeat

We can store the URL and the summary generated
We can add control to the users to ask the bot to regenerate
'''


with open('.key') as f:
    text = f.read().strip()

keys = ast.literal_eval(text)

conn = sqlite3.connect("database.db")


logging.basicConfig(filename='botlog.log', encoding='utf-8', level=logging.DEBUG, filemode='a', format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger()

def summarize(url):
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM mytable WHERE URL = ?', (url,))
    result = cursor.fetchone()[0]
    if result > 0:
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
    else:
        cursor.execute('SELECT Text FROM mytable WHERE URL = ?', (url,))
        result = cursor.fetchone()
        return result[0]

def create_api():
    try:
        api = Mastodon(access_token='summarizerbot_usercred.secret')
    except Exception as e:
        logger.error("Error creating API", exc_info=True)
        raise e
    logger.info("API created")
    return api


def check_mentions(api, since_id):
    logger.info("Retrieving mentions")
    new_since_id = since_id if not since_id is None else -14

    for notif in api.notifications(types=['mention']):
        new_since_id = max(notif['id'], since_id)
        if notif['status']['in_reply_to_id'] is None:
            continue
        content = api.status(notif['status']['in_reply_to_id'])
        url = extract_url(content['content'])
        logger.info(f"Answering to {notif['account']}")
        if url:
            summary = summarize(url)
            api.status_post(summary, in_reply_to_id=notif['status']['id'])
            time.sleep(61)
            with open('.lastid', 'w') as f:
                print(new_since_id)
                f.write(f'{new_since_id}')
            logger.info("tooted a summary")
            continue

def extract_url(content):
    '''
    we shall only summarize first URL for now
    '''
    soup = BeautifulSoup(content)
    try:
        url = [a for a in soup.find_all('a') if a.get('class') is None]
        return url[0].get('href')
    except:
        return None


def main():
    api = create_api()

    while True:
        with open('.lastid') as f:
            since_id = int(f.read().strip())
        check_mentions(api, since_id)
        logger.info("Waiting...")
        time.sleep(60)

if __name__ == "__main__":
    main()

    #api = create_api()

    
