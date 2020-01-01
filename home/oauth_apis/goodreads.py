import datetime
import requests
import xml.etree.ElementTree as ET

from .exceptions import stat_exception_override
from secret import GOODREADS_KEY
from secret import GOODREADS_USERID

from models import Stat

class GoodreadsAPI(object):

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

        return Stat(
            stat_id="read_current_year",
            description="Books I read this year",
            value=titles
        )


    def get_books_read_last_year():
        # TODO this is almost identical to get_books_read_this_year, needs refactoring.
        year = datetime.date.today().year - 1
        resp = requests.get(f"https://www.goodreads.com/review/list?key={GOODREADS_KEY}&v=2&read_at={year}&id={GOODREADS_USERID}")
        root = ET.fromstring(resp.content)

        books = root.findall('./reviews/review/book')
        titles = []
        for book in books:
            title = book.findall('./title')[0].text
            author = book.findall('./authors/author/name')[0].text
            titles.append(f"{title} - {author}")

        return Stat(
            stat_id="read_prev_year",
            description="Books I read last year",
            value=titles
        )

    def get_currently_reading():
        resp = requests.get(f"https://www.goodreads.com/review/list?key={GOODREADS_KEY}&v=2&shelf=currently-reading&id={GOODREADS_USERID}")
        root = ET.fromstring(resp.content)
        title = root.findall("./reviews/review/book/title")[0].text

        return Stat(
            stat_id="currently_reading",
            description="Reading",
            value=title
        )



    @classmethod
    @stat_exception_override("goodreads")
    def get_stats(klass):
        stats = [
            klass.get_currently_reading(),
            klass.get_books_read_this_year(),
            klass.get_books_read_last_year()
        ]
        return stats
