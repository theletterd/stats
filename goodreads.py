import asyncio
import datetime
from aiohttp_requests import requests
import xml.etree.ElementTree as ET

from secret import GOODREADS_KEY
from secret import GOODREADS_USERID


async def get_request(url):
    response = await requests.get(url)
    return response

async def get_books_read_this_year():
    current_year = datetime.date.today().year
    print("getting books this year")
    resp = await requests.get(f"https://www.goodreads.com/review/list?key={GOODREADS_KEY}&v=2&read_at={current_year}&id={GOODREADS_USERID}")
    content = await resp.text()
    print("got books this year")
    root = ET.fromstring(content)

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

async def get_books_read_last_year():
    year = datetime.date.today().year - 1
    print("getting books last year")
    resp = await requests.get(f"https://www.goodreads.com/review/list?key={GOODREADS_KEY}&v=2&read_at={year}&id={GOODREADS_USERID}")
    content = await resp.text()
    print("got books last year")
    root = ET.fromstring(content)

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

async def get_currently_reading():
    print("getting currently_reading")
    resp = await requests.get(f"https://www.goodreads.com/review/list?key={GOODREADS_KEY}&v=2&shelf=currently-reading&id={GOODREADS_USERID}")
    print("got currently_reading")
    content = await resp.text()
    root = ET.fromstring(content)
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


async def poop():
    results = await asyncio.gather(
        get_books_read_this_year(),
        get_books_read_last_year(),
        get_currently_reading()
    )
    return results
