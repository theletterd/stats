import xml.etree.ElementTree as ET
from tools.util import today_pacific

from flask import current_app

from . import oauth
oauth.register(
    name='goodreads',
    request_token_url='https://www.goodreads.com/oauth/request_token',
    access_token_url='https://www.goodreads.com/oauth/access_token',
    authorize_url='https://www.goodreads.com/oauth/authorize',
    api_base_url='https://www.goodreads.com/'
)

GOODREADS_KEY = current_app.config['GOODREADS_CLIENT_ID']
GOODREADS_USERID = current_app.config['GOODREADS_USERID']

from models import Stat

class GoodreadsAPI(object):

    def get_books_read_this_year():
        current_year = today_pacific().year
        return Stat(
            stat_id="read_current_year",
            description="Books I read this year",
            value=GoodreadsAPI._get_book_titles_for_year(current_year)
        )

    def get_books_read_last_year():
        year = today_pacific().year - 1
        return Stat(
            stat_id="read_prev_year",
            description="Books I read last year",
            value=GoodreadsAPI._get_book_titles_for_year(year)
        )

    def _get_book_titles_for_year(year):
        params = {
            'read_at': year,
            'v': '2',
            'key': GOODREADS_KEY,
            'id': GOODREADS_USERID,
            'format': 'xml'
        }
        resp = oauth.goodreads.get('review/list', params=params)
        root = ET.fromstring(resp.content)

        books = root.findall('./reviews/review/book')
        titles = []
        for book in books:
            title = book.findall('./title')[0].text
            author = book.findall('./authors/author/name')[0].text
            titles.append(f"{title} - {author}")

        return titles

    def get_currently_reading():
        params = {
            'v': '2',
            'key': GOODREADS_KEY,
            'id': GOODREADS_USERID,
            'format': 'xml',
            'shelf': 'currently-reading'

        }
        resp = oauth.goodreads.get('review/list', params=params)
        root = ET.fromstring(resp.content)
        title = root.findall("./reviews/review/book/title")[0].text

        return Stat(
            stat_id="currently_reading",
            description="Reading",
            value=title
        )

    @classmethod
    def get_stat_getters(klass):
        stat_getters = [
            klass.get_currently_reading,
            klass.get_books_read_this_year,
            klass.get_books_read_last_year
        ]
        return stat_getters
