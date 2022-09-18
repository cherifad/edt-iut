import json
from deepdiff import DeepDiff
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
from dateutil import parser

food_data = {}
edt_data = {}


def load_files():
    global food_data
    global edt_data
    with open("./data/INFO_2_new.json", "r") as f:
        food_data = json.load(f)

    with open("./data/INFO_2.json", "r") as f:
        edt_data = json.load(f)


# initializations
cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# adding first data
food_ref = db.collection('food')
edt_ref = db.collection('edt')
today = datetime.today().date()


def populate_food_db():
    for single in food_data['data']:
        folder = food_ref.document(f"{single['date']}_{single['Type'].replace(' ', '_')}")
        folder.set({
            'date': single['date'],
            'day': single['Jour'],
            'moment': single['Moment'],
            'type': single['Type'],
            'food': single['Plats']
        })


def populate_edt_db():
    print("Populating edt db")
    for single in edt_data:
        print(single)
        for course in edt_data[single]:
            print(course)
            folder = edt_ref.document("2-INFO").collection(f"{single}").document(f"{course['id']}")
            folder.set({
                'begin': course['begin'],
                'color': course['color'],
                'description': course['description'],
                'duration': course['duration'],
                'end': course['end'],
                'location': course['location'],
                'name': course['name'],
                'prof': course['prof'],
            })


def wipe_food_db():
    docs = food_ref.stream()
    for doc in docs:
        food_ref.document(doc.id).delete()


def wipe_edt_db():
    docs = edt_ref.stream()
    for doc in docs:
        edt_ref.document(doc.id).delete()


def check_date(item):
    if parser.parse(item['begin']).date() >= today:
        return True
    return False


def get_differences(file1, file2):
    with open(file1, "r") as f:
        data1 = json.load(f)
    with open(file2, "r") as f:
        data2 = json.load(f)

    groups_1 = []
    groups_2 = []

    for single in data1:
        groups_1.append(single)
    for single in data2:
        groups_2.append(single)

    for group in groups_1:
        data1[group] = filter(check_date, data1[group])
        data1[group] = list(data1[group])
        data1[group] = sorted(data1[group], key=lambda k: k['begin'])

    for group in groups_2:
        data2[group] = filter(check_date, data2[group])
        data2[group] = list(data2[group])
        data2[group] = sorted(data2[group], key=lambda k: k['begin'])

    return DeepDiff(data1, data2, ignore_order=True)


supported_edt = [
    {
        'name': "INFO_1",
        'url': "https://ade6-usmb-ro.grenet.fr/jsp/custom/modules/plannings/direct_cal.jsp?data=1b9e1ac2a1720dfd6bd1d42ad86c77f9c55ef35a53135e0070a97be8b09957efa9a0e9cb08b4730b&resources=5698,5696,5695,5694,5693,5692,5691,5639&projectId=4&calType=ical&lastDate=2040-08-14",
    },
    {
        'name': "INFO_2",
        'url': "https://ade6-usmb-ro.grenet.fr/jsp/custom/modules/plannings/direct_cal.jsp?data=1b9e1ac2a1720dfd6bd1d42ad86c77f9c55ef35a53135e0070a97be8b09957efa9a0e9cb08b4730b&resources=2663,5709,5707,5703&projectId=4&calType=ical&lastDate=2040-08-14",
    },
    {
        'name': "GEA_1",
        'url': "https://ade6-usmb-ro.grenet.fr/jsp/custom/modules/plannings/direct_cal.jsp?data=1b9e1ac2a1720dfd6bd1d42ad86c77f9c55ef35a53135e0070a97be8b09957efa9a0e9cb08b4730b&resources=5841,5840,5873,5872,5851,5848,5859,5853&projectId=4&calType=ical&lastDate=2040-08-14",
    },
    {
        'name': "GEA_2",
        'url': "https://ade6-usmb-ro.grenet.fr/jsp/custom/modules/plannings/direct_cal.jsp?data=1b9e1ac2a1720dfd6bd1d42ad86c77f9c55ef35a53135e0070a97be8b09957efa9a0e9cb08b4730b&resources=3259,3277,3200,3219,3282,3308,3615,3230,3242&projectId=4&calType=ical&lastDate=2040-08-14",
    },
]

