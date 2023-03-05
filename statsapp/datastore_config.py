CACHE_CONFIG = {
    'CACHE_TYPE': 'MemcachedCache',
    'CACHE_DEFAULT_TIMEOUT': 10,
    'CACHE_MEMCACHED_SERVERS': ['localhost:20583'],
    'CACHE_KEY_PREFIX': 'stats_app_stats'
}

DB_CONFIG = {
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///./sqlite_database',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False
}
