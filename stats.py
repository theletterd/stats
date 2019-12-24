import pprint

from flask import Flask
from flask import jsonify
from flask import render_template

import goodreads
import gsheet

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

stat_cache = {}

WEIGHT_STAT_GROUPS = [
    [
        'weight_lbs_recent',
    ],
    [
        'weight_lbs_min_current_year', 
        'weight_lbs_max_current_year'
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

@app.route("/")
def root():
    return render_template('index.html', stats=stat_cache)

@app.route("/data")
def data():
    populate_stats()
    
    stats = {
        'misc_stats': {
            'stats': get_populated_stat_groups(MISC_STAT_GROUPS),
            'description': "Miscellaneous Stats"
        },
        'step_stats': {
            'stats': get_populated_stat_groups(STEP_STAT_GROUPS),
            'description': 'Steps'
        },
        'weight_stats': {
            'stats': get_populated_stat_groups(WEIGHT_STAT_GROUPS),
            'description' : 'Weight (lbs)'
        },
    }
    return jsonify(stats)

def get_populated_stat_groups(stat_groups):
    return [[stat_cache[stat] for stat in stat_group] for stat_group in stat_groups]
            

def populate_stats():
    if not stat_cache:
        goodread_stats = goodreads.get_stats()
        gsheet_stats = gsheet.get_stats()
        
        stat_cache.update(goodread_stats)
        stat_cache.update(gsheet_stats)
    pprint.pprint(stat_cache)
        
        
    

if __name__ == '__main__':
    app.run(debug=True)
