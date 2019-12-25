MEMCACHED_PORT = 20583
MEMCACHED_STATS_KEY = 'stats_app_stats'

WEIGHT_STAT_GROUPS = [
    [
        'weight_lbs_recent',
    ],
    [
        'weight_lbs_min_current_year', 
        'weight_lbs_avg_current_year',
        'weight_lbs_max_current_year'
    ],
    [
        'weight_lbs_min_prev_year', 
        'weight_lbs_avg_prev_year',
        'weight_lbs_max_prev_year'
    ]
]

MISC_STAT_GROUPS = [
    [
        'age',
        'height',
        'wife_count',
        'married_years',
        'children_count',
    ],
    [
        'currently_reading',
        'birkenstock_count',    
    ],
    [
    'tshirt_size',
    'shoe_size_us_mens',
    'shoe_size_us_womens',
    'dress_size_us',
    ]
]

STEP_STAT_GROUPS = [
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

