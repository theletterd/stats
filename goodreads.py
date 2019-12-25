import datetime
import requests
import xml.etree.ElementTree as ET

from secret import GOODREADS_KEY
from secret import GOODREADS_USERID


def get_books_read_this_year():
    current_year = datetime.date.today().year
    resp = requests.get(f"https://www.goodreads.com/review/list?key={GOODREADS_KEY}&v=2&read_at={current_year}&id={GOODREADS_USERID}")
    root = ET.fromstring(resp.content)

    books = root.findall('./reviews/review/book')
    titles = []
    for book in books:
        title = book.findall('./title')[0].text
        author = book.findall('./authors/author/name')[0].text
        titles.append(f"{title} - {author}")

    stats = {
        'read_current_year': dict(
            stat_id="read_current_year", 
            description="Books I read this year", 
            value=titles, 
        )
    }

    return stats

def get_books_read_last_year():
    year = datetime.date.today().year - 1
    resp = requests.get(f"https://www.goodreads.com/review/list?key={GOODREADS_KEY}&v=2&read_at={year}&id={GOODREADS_USERID}")
    root = ET.fromstring(resp.content)

    books = root.findall('./reviews/review/book')
    titles = []
    for book in books:
        title = book.findall('./title')[0].text
        author = book.findall('./authors/author/name')[0].text
        titles.append(f"{title} - {author}")

    stats = {
        'read_prev_year': dict(
            stat_id="read_prev_year", 
            description="Books I read last year", 
            value="<br>".join(titles), 
        )
    }

    return stats

def get_currently_reading():
    resp = requests.get(f"https://www.goodreads.com/review/list?key={GOODREADS_KEY}&v=2&shelf=currently-reading&id={GOODREADS_USERID}")
    root = ET.fromstring(resp.content)
    title = root.findall("./reviews/review/book/title")[0].text
    image_url = root.findall("./reviews/review/book/image_url")[0].text

    stats = {
        'currently_reading': dict(
            stat_id="currently_reading", 
            description="Reading", 
            value=title, 
            image_url=image_url)
    }

    return stats


def get_stats():
    stats = {}
    stats.update(get_currently_reading())
    stats.update(get_books_read_this_year())
    stats.update(get_books_read_last_year())
    return stats
