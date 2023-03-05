CACHE_TYPE = 'memcached'
CACHE_DEFAULT_TIMEOUT = 10 # 60 * 60 * 24
CACHE_MEMCACHED_SERVERS = ['localhost:20583']
CACHE_KEY_PREFIX = 'stats_app_stats'


SQLALCHEMY_DATABASE_URI = 'sqlite:///./sqlite_database'
SQLALCHEMY_TRACK_MODIFICATIONS = False

OAUTH1_SERVICES = {'goodreads'}
