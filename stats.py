from flask import Flask
from flask import jsonify
from flask import render_template

import goodreads
import gsheet

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

stat_cache = {}


BASIC_STATS = [
    'age',
    'children_count',
    'birkenstock_count',    
]

@app.route("/")
def root():
    return render_template('index.html', stats=stat_cache)

@app.route("/data")
def data():
    populate_stats()
    
    stats = {'basic_stats': [stat_cache[stat] for stat in BASIC_STATS]}
    return jsonify(stats)

def populate_stats():
    if not stat_cache:
        goodread_stats = goodreads.get_stats()
        gsheet_stats = gsheet.get_stats()

        
        stat_cache.update(goodread_stats)
        stat_cache.update(gsheet_stats)
        
        
    

if __name__ == '__main__':
    app.run()
