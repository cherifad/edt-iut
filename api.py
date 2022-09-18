from flask import Flask
from flask_marshmallow import Marshmallow
import json
from datetime import datetime
from edt_parser import get_ics
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
ma = Marshmallow(app)

last_update = None


def getAllEdt():
    global last_update
    for edt in supported_edt:
        get_ics(edt['url'], edt['name'])
        last_update = datetime.now()


@app.route('/<group>')
def get_edt(group):
    try:
        with open(f'./data/{group}.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        return {"message": "File not found"}, 404
    return {'data': data}, 200


@app.route('/info/supported_edt')
def get_supported_edt():
    data = []
    for i in range(len(supported_edt)):
        data.append(supported_edt[i]['name'])
    return {'data': data}, 200


@app.route('/info/last_update')
def get_last_update():
    return {'data': last_update}, 200


supported_edt = [
    {
        'name': "INFO_1",
        'url': "https://ade6-usmb-ro.grenet.fr/jsp/custom/modules/plannings/direct_cal.jsp?data=1b9e1ac2a1720dfd6bd1d42ad86c77f9c55ef35a53135e0070a97be8b09957efa9a0e9cb08b4730b&resources=5698,5696,5695,5694,5693,5692,5691,5639&projectId=4&calType=ical&lastDate=2040-08-14"
    },
    {
        'name': "INFO_2",
        'url': "https://ade6-usmb-ro.grenet.fr/jsp/custom/modules/plannings/direct_cal.jsp?data=1b9e1ac2a1720dfd6bd1d42ad86c77f9c55ef35a53135e0070a97be8b09957efa9a0e9cb08b4730b&resources=2663,5709,5707,5703&projectId=4&calType=ical&lastDate=2040-08-14",
    },
]

scheduler = BackgroundScheduler(timezone='Europe/Paris', day_of_week='mon-fri', hour=8, minute=0)
scheduler.add_job(func=getAllEdt)

if __name__ == '__main__':
    scheduler.start()
    scheduler.print_jobs()
    app.run()  # run our Flask app

