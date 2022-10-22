import requests as rq
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
import dateparser
from datetime import datetime as date
from datetime import timedelta
import re
import json
import warnings

# Ignore dateparser warnings regarding pytz
warnings.filterwarnings(
    "ignore",
    message="The localize method is no longer necessary, as this time zone supports the fold attribute",
)

url = "https://www.crous-grenoble.fr/restaurant/ru-dannecy/"

moment_journee = ['Matin', 'Midi', 'Soir']

day_of_week_FR = [
    'Lundi',
    'Mardi',
    'Mercredi',
    'Jeudi',
    'Vendredi'
]

food_list = []


class Menu:
    def __init__(self, date, day, moment, type_food, food):
        self.date = date
        self.day = day
        self.moment = moment
        self.type_food = type_food
        self.food = food

    def to_dict(self):
        return {'date': str(self.date),
                'Jour': self.day,
                'Moment': self.moment,
                'Type': self.type_food,
                'Plats': self.food}


def Online(url):
    online = True
    try:
        webUrl = urlopen(url)
        print("result code: " + str(webUrl.getcode()) + " --> Site accessible")
        if webUrl.getcode() != 200:
            online = False
    except:
        online = False
    return online


def ExtractDate(string):
    menu_date = date.today()

    m = re.search(r"\d", string)

    if m:
        date_string = string[m.start():]
        menu_date = dateparser.parse(date_string).date()

    return menu_date


def ExtractTitle(url):
    # grab web page
    response = rq.get(url)

    # parse it to html
    soup = bs(response.text, 'html.parser')

    # Page title
    title = soup.find('title').text.replace(" ", "_")

    return title


# if 'DT' --> current date with time else --> current date only
def FormatedDateTime(choice=''):
    value = ''
    if choice.upper() == 'DT':
        now = date.now()
        value = now.strftime("%Y-%m-%d %H-%M").replace(" ", "_")
    elif choice.upper() == 'D':
        now = date.now()
        value = now.strftime("%Y-%m-%d")
    else:
        now = date.now()
        value = now.strftime("%H-%M").replace(" ", "_")

    return value


def Infos(url):
    food_list = []

    if Online(url):

        # grab web page
        response = rq.get(url)

        # parse it to html
        soup = bs(response.text, 'html.parser')

        # find menu location
        week_menu = soup.find(id='menu-repas').find(class_='slides')

        # grab all menus from the day
        single_day = week_menu.findChildren("li", recursive=False)

        # browse all days of the week
        for day in single_day:

            date_and_date = day.find('h3').text.upper()

            # default day of week
            menu_day = 'inconnu !'

            # find day of week about the menu
            for day_week in day_of_week_FR:  # reference to the list of day
                if date_and_date.find(day_week.upper()) != -1:  # Finf return -1 if not found
                    menu_day = day_week  # if found set to the date

            date_formated = ExtractDate(date_and_date)

            # travailler avec le menu sans la date
            single_day_menu = day.find(class_='content clearfix')

            # récupérer le menu du matin, du midi ou du soir
            single_day_menu_moment = single_day_menu.findChildren("div", recursive=False)

            for moment in single_day_menu_moment:

                # Day of the week
                menu_moment = moment_journee[single_day_menu_moment.index(moment)]

                # type de self (matin, self traditionnel, self pâte, ...)
                type_self = moment.find_all(class_='content-repas')

                # liste des plats
                liste_plat = moment.find_all(class_='liste-plats')

                type_plats = []

                for i in type_self:
                    type_plats = i.find_all(class_='name')

                for x in range(len(type_plats)):
                    try:
                        list_plat_type_txt = []

                        for plat in liste_plat[x].find_all('li'):
                            list_plat_type_txt.append(plat.text)

                        food_list.append(
                            Menu(date_formated, menu_day, menu_moment, type_plats[x].text, list_plat_type_txt))

                    except:
                        pass
    else:
        print('Unable to retrieve data')

    return food_list


def GenerateJson(url, filename):
    name = ''

    try:
        food_list = Infos(url)

        results = {
            "data": [food.to_dict() for food in food_list],
            'info': {
                'date': str(date.utcnow() + timedelta(hours=2)).replace(" ", "T"),
                'name': ExtractTitle(url)
            }
        }

        name = './data/{}_{}.'.format(ExtractTitle(url), FormatedDateTime('dt'))

        # with open('{}pkl'.format(name), 'wb') as outp:
        #    pickle.dump(food_list, outp, pickle.HIGHEST_PROTOCOL)

        jsdata = json.dumps(results, sort_keys=True, ensure_ascii=False, indent=4)

        with open('./data/{}.json'.format(filename), 'w') as outfile:
            outfile.write(jsdata)

        print('Files generated successfully at {}'.format(name))

    except Exception as e:
        print(e)
        print('Unable to generate files')

    return '{}pkl'.format(name)