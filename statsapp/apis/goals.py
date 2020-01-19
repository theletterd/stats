import requests

from statsapp.tools.util import today_pacific

URL_FORMAT = "https://goals.theletterd.co.uk/year/{year}"

class GoalsAPI(object):

    def get_goals_data():
        year = today_pacific().year
        url = URL_FORMAT.format(year=year)
        resp = requests.get(url)
        return resp.json()
