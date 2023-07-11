from bs4 import BeautifulSoup
from newspaper import Article
import cohere
import logging
import ast
from mastodon import Mastodon
import time
import sqlite3

'''
TODO: 
    - We can add control to the users to ask the bot to regenerate
'''


with open('.key') as f:
    text = f.read().strip()

keys = ast.literal_eval(text)

conn = sqlite3.connect("database.db")


logging.basicConfig(filename='botlog.log', encoding='utf-8', level=logging.DEBUG, filemode='a', format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger()

def summarize(url, calling):
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM generations WHERE URL = ?', (url,))
    result = cursor.fetchone()[0]
    print(url)
    if result == 0:
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
        cursor.execute('''
                INSERT INTO generations (URL, Text, Tries, Calling)
                VALUES (?, ?, ?, ?)
                ''', (url, response.summary, 0, calling))

        # Save the changes and close the connection
        conn.commit()
        return response.summary
    else:
        cursor.execute('SELECT Text FROM generations WHERE URL = ?', (url,))
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


def check_mentions(api):
    logger.info("Retrieving mentions")

    for notif in api.notifications(types=['mention']):
        if notif['status']['in_reply_to_id'] is None:
            continue
        content = api.status(notif['status']['in_reply_to_id'])
        url = extract_url(content['content'])
        logger.info(f"Answering to {notif['account']}")
        if url:
            summary = summarize(url, notif['status']['id'])
            api.status_post(summary, in_reply_to_id=notif['status']['id'])
            time.sleep(61)
            logger.info("tooted a summary")
            continue
    api.notifications_clear()

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
    cursor = conn.cursor()

    while True:
        check_mentions(api)
        logger.info("Waiting...")
        time.sleep(60)

if __name__ == "__main__":
    main()

    #api = create_api()

    
