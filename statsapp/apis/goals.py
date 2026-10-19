import requests
import logging

from statsapp.tools.util import today_pacific

URL_FORMAT = "https://goals.theletterd.co.uk/year/{year}"
REQUEST_TIMEOUT_SECONDS = 5

class GoalsAPI(object):

    def get_goals_data():
        year = today_pacific().year
        url = URL_FORMAT.format(year=year)
        try:
            resp = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            logging.warning("Failed to fetch goals data from %s: %s", url, e)
            return None
