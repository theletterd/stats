from flask import Flask
from flask import jsonify
from flask import render_template

import goodreads
import gsheet

app = Flask(__name__)


@app.route("/")
def root():
    return "oh hi there" #render_template('index.html')

@app.route("/data")
def data():
    goodread_stats = goodreads.get_stats()
    gsheet_stats = gsheet.get_stats()

    stats = {}
    stats.update(goodread_stats)
    stats.update(gsheet_stats)
    return jsonify(stats)

if __name__ == '__main__':
    app.run()
