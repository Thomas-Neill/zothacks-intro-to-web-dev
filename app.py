from flask import Flask
from flask import request, send_from_directory
from flask.templating import render_template
from flask_cors import CORS
import sqlite3 as sl
import datetime
import requests

app = Flask(__name__)
CORS(app)


waitingOthers = []

@app.route("/<path:path>",methods=['GET'])
def hi(path):
    return send_from_directory('frontend',path)

@app.route("/search/",methods=['GET'])
def search():
    conn = sl.connect('menu.db')
    cur = conn.cursor()
    #print('searched')
    place = request.args.get('place')
    keyword = request.args.get('keyword')
    foodtype = request.args.get('types')
    cals = request.args.get('calories')
    vegan = request.args.get('vegan')
    vege = request.args.get('vegetarian')
    meal = request.args.get('meal')

    query = "SELECT * FROM menu"

    constraints = [f"date='{datetime.date.today()}'"]

    if cals != '-1':
        constraints.append(f"calories<{cals}")
    if vegan != "false":
        constraints.append(f"vega=1")
    if vege != "false":
        constraints.append(f"vege=1")
    mealMap = {'dinner':107,'breakfast':49,'brunch':2651,'lunch':106}
    Periods = {107:'dinner',49:'breakfast',2651:'brunch',106:'lunch'}
    if meal:
        ms = meal.split(",")

        constraints.append("(" + " OR ".join(f"meal={mealMap[m.lower()]}" for m in ms) + ")")
    if keyword != "":
        constraints.append(f"name LIKE '%{keyword}%'")
    if foodtype != "":
        fs = foodtype.split(",")
        constraints.append("(" + " OR ".join(f"foodtype LIKE '%{f}%'" for f in fs) + ")")
    if place != "":
        constraints.append(f"area LIKE '%{place}%'")
    
    query = query + " WHERE " + " AND ".join(constraints) #no sql injection plz (;_;)
    #print(query)

    res = {"body":[]}
    for i in cur.execute(query):
        res['body'].append({
            'date': i[0],
            'area': i[1],
            'station': i[2],
            'meal': Periods[int(i[3])],
            'name': i[4],
            'calories': i[5],
            'blurb': i[6],
            'vege': i[7],
            'vega':i[8]
        })
    return res


@app.route('/auto/',methods=['GET'])
def autocomplete():
    conn = sl.connect('menu.db')
    cur = conn.cursor()
    C = request.args.get('q')

    query = f"SELECT DISTINCT name FROM menu WHERE name LIKE '%{C}%' LIMIT 5"

    return {'body':list(i[0] for i in cur.execute(query))}

apiKey = "24442074-8042608e9c23ab8f856de31c7"

@app.route('/pics/',methods=['GET'])
def fetchPicture():
    q=request.args.get('q')
    res = requests.get(f"https://pixabay.com/api/?key={apiKey}&q={q}&category=food&perPage=1")
    return res.text
