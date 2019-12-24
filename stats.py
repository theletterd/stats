import pprint

from flask import Flask
from flask import jsonify
from flask import render_template

import goodreads
import gsheet

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

stat_cache = {}

WEIGHT_STATS = [

]

MISC_STATS = [
    'age',
    'height',
    'wife_count',
    'married_years',
    'children_count',
    'birkenstock_count',    
#    'recent_weight_lbs',
    'currently_reading',
    'tshirt_size'
]

STEP_STATS = [
    'step_count_today',
    'step_count_yesterday',
    'distance_miles_today',
    'distance_miles_yesterday',
]

STEP_YEAR_STATS = [
    'step_count_current_year',
    'step_count_prev_year',
]

@app.route("/")
def root():
    return render_template('index.html', stats=stat_cache)

@app.route("/data")
def data():
    populate_stats()
    
    stats = {
        'misc_stats': {
            'stats': [stat_cache[stat] for stat in MISC_STATS],
            'description': "Miscellaneous Stats"
            },
        'step_stats': {
            'stats': [stat_cache[stat] for stat in STEP_STATS],
            'description': 'Steps'
            },
        'step_year_stats': {
            'stats': [stat_cache[stat] for stat in STEP_YEAR_STATS],
            },
        }
    return jsonify(stats)


def populate_stats():
    if not stat_cache:
        goodread_stats = goodreads.get_stats()
        gsheet_stats = gsheet.get_stats()
        
        # derived_stats - this should all be moved to the gsheet lib?
        weight_lbs = float(gsheet_stats['weight_kg_recent']['value']) / 0.454
        recent_weight_lbs = {
            'stat_id': 'recent_weight_lbs',
            'description': 'Recent Weight (lbs)',
            'value': f"{weight_lbs:.1f}"
        }
        gsheet_stats['recent_weight_lbs'] = recent_weight_lbs
        
        stat_cache.update(goodread_stats)
        stat_cache.update(gsheet_stats)
    pprint.pprint(stat_cache)
        
        
    

if __name__ == '__main__':
    app.run(debug=True)
