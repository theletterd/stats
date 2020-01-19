from statsapp.models.stat import Stat
from statsapp.apis.goodreads import GoodreadsAPI
from statsapp.tools.util import today_pacific


class GoodreadsStats(object):

    def get_stats(user):
        # TODO so we're not actually doing anything with user.
        # Goodreads' API doesn't use oauth for getting stuff off the shelves,
        # which is annoying, so we need to separately store the goodreads userid.
        # right now that's just duncan's :D but if we want to expand this further, we'll
        # need to store goodreads user_ids somewhere other than a config.

        return [
            GoodreadsStats._get_books_read_last_year(),
            GoodreadsStats._get_books_read_this_year(),
            GoodreadsStats._get_currently_reading(),
        ]

    def _get_books_read_last_year():
        year = today_pacific().year - 1

        titles = GoodreadsAPI.get_books_read_for_year(year)
        return Stat(
            stat_id="read_prev_year",
            description="Books I read last year",
            value=titles
        )

    def _get_books_read_this_year():
        current_year = today_pacific().year
        titles = GoodreadsAPI.get_books_read_for_year(current_year)
        return Stat(
            stat_id="read_current_year",
            description="Books I read this year",
            value=titles
        )

    def _get_currently_reading():
        title = GoodreadsAPI.get_currently_reading()
        return Stat(
            stat_id="currently_reading",
            description="Reading",
            value=title
        )
