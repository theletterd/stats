from oauth_apis.strava import StravaAPI

class StravaStats(object):

    def get_stats(user):
        return StravaAPI.get_stats()
