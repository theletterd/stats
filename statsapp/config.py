MEMCACHED_PORT = 20583
MEMCACHED_STATS_KEY = 'stats_app_stats'

SQLALCHEMY_DATABASE_URI = 'sqlite:///./sqlite_database'
SQLALCHEMY_TRACK_MODIFICATIONS = False

OAUTH1_SERVICES = {'goodreads'}


WEIGHT_STAT_GROUPS = {
    'description': 'Weight (lbs)',
    'stat_group_id': 'weight_stats',
    'stat_groups': [
        ['weight_lbs_recent'],
        [
            'weight_lbs_min_current_year',
            'weight_lbs_avg_current_year',
            'weight_lbs_max_current_year'
        ],
        [
            'weight_lbs_min_prev_year',
            'weight_lbs_avg_prev_year',
            'weight_lbs_max_prev_year',
        ]
    ]
}

BOOK_STAT_GROUPS = {
    'description': 'Books',
    'stat_group_id': 'book_stats',
    'stat_groups': [
        ['currently_reading'],
        [
            'read_current_year',
            'read_prev_year'
        ],
    ]
}

MISC_STAT_GROUPS = {
    'description': 'Miscellaneous Stats',
    'stat_group_id': 'misc_stats',
    'stat_groups': [
        [
            'age',
            'height',
            'wife_count',
            'married_years',
            'children_count',
            'birkenstock_count',
        ],
        [
            'piercings_current',
            'piercing_instances',
            'tattoo_count',
            'surgery_count'
        ],
        [
            'tshirt_size',
            'shoe_size_us_mens',
            'shoe_size_us_womens',
            'dress_size_us',
            'max_pullup_count'
        ],
    ]
}

STEP_STAT_GROUPS = {
    'description': 'Steps',
    'stat_group_id': 'step_stats',
    'stat_groups': [
        [
            'step_count_today',
            'step_count_yesterday',
            'distance_miles_today',
            'distance_miles_yesterday',
        ],
        [
            'step_count_current_year',
            'step_count_prev_year',
        ],
        [
            'distance_miles_current_year',
            'distance_miles_prev_year',
        ]
    ]
}

RUNNING_STAT_GROUPS = {
    'description': 'Runs',
    'stat_group_id': 'run_stats',
    'stat_groups': [
        [
            'run_count_current_year',
            'run_count_prev_year',
        ],
        [
            'distance_run_current_year_miles',
            'distance_run_prev_year_miles',
        ]
    ]
}
