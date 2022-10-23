import json
import random
import re
import time
import requests
from ics import Calendar
import requests

supported_edt = [
    {
        'name': "INFO_1",
        'url': "https://ade6-usmb-ro.grenet.fr/jsp/custom/modules/plannings/direct_cal.jsp?data=1b9e1ac2a1720dfd6bd1d42ad86c77f9c55ef35a53135e0070a97be8b09957efa9a0e9cb08b4730b&resources=5698,5696,5695,5694,5693,5692,5691,5639&projectId=4&calType=ical&lastDate=2040-08-14"
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


def get_ics(url: str, filename: str):
    print("Downloading...")
    print(f"URL: {url}")
    r = requests.get(url, allow_redirects=True)
    open(f"./data/{filename}.ics", 'wb').write(r.content)
    print("Downloaded")
    try:
        len(js_colors[filename])
    except KeyError:
        js_colors[filename] = []

    to_json(filename)


event_list = []
json_list = {}
group_list = []
course_list = []
colors = {}
colors_array = ["#cdb4db", "#ffc8dd", "#ffafcc", "#bde0fe", "#a2d2ff", "#006d77", "#83c5be", "#edf6f9", "#ffddd2",
                "#e29578"]
used_colors = []


def random_color(course, filename):
    global used_colors
    global colors_array
    color = "#000000"
    if len(colors_array) == 0:  # If no more colors available
        colors_array = used_colors  # Reset colors
        used_colors = []  # Reset used colors
    if not js_colors[filename]:
        color = random.choice(colors_array)  # Pick a random color
        js_colors[filename].append({
            'color': color,
            'course': course
        })  # Add color to js_colors
        used_colors.append(color)  # Add color to used colors
        colors_array.remove(color)  # Remove color from available colors
    else:
        ok = True
        for i in js_colors[filename]:
            if i['course'] == course:
                color = i['color']
                ok = False
        if ok:
            color = random.choice(colors_array)  # Pick a random color
            js_colors[filename].append({
                'color': color,
                'course': course
            })  # Add color to js_colors
            used_colors.append(color)  # Add color to used colors
            colors_array.remove(color)  # Remove color from available colors

    return color


with open("./data/colors.json", encoding='ISO-8859-1') as f:
    js_colors = json.load(f)


def group_detector(query: str, grade: str):
    ## for INFO_1
    info1_pattern = re.compile(r"[0-9]+-[a-zA-Z]+-[0-9]{2}", re.IGNORECASE)
    ## for INFO_2
    info2_pattern = re.compile(r"[0-9]+-[a-zA-Z]+-[0-9]{1}", re.IGNORECASE)
    try:
        if grade == "INFO_1":
            group = re.search(info1_pattern, query).group(0)
        elif grade == "INFO_2":
            group = re.search(info2_pattern, query).group(0)
        else:
            group = query
        if group not in group_list:
            group_list.append(group)
    except Exception as e:
        group = "Inconnu"
    return group


def to_json(filename: str):
    global colors_array, used_colors
    print("Parsing...")
    with open(f"data/{filename}.ics", "r") as file:
        c = Calendar(file.read())
        print("ics file loaded")

    print("Parsing...")

    id = 0

    for event in c.events:
        name = event.name.replace("_", " ")
        pattern = re.compile(r"[A-Z]+[0-9]+.[0-9]+")
        course = name[0:5]
        if course not in course_list:
            course_list.append(course)  # Add course to list
            colors[course] = random_color(course, filename)  # Add color to course
        begin = event.begin
        end = event.end
        duration = event.duration
        location = event.location
        description = event.description

        # pattern to find the professor name
        pattern = re.compile(r"[0-9]+(\s(.+\s)+)\(")
        try:
            prof = re.search(pattern, str(event.description)).group(1)
            prof = prof.replace('\n', '')
        except:
            prof = "Inconnu"

        group = group_detector(event.description, filename)

        if group not in group_list:
            for group in group_list:  # If group is in group_list... so if it's a CM
                try:
                    # if the group is already in the list
                    json_list[group].append({
                        'id': id,
                        'name': name,
                        'begin': str(begin),
                        'end': str(end),
                        'duration': str(duration),
                        'location': location,
                        'description': description,
                        'prof': prof,
                        'color': str(colors[course]),
                    })
                except:
                    # if the group is not in the list
                    json_list[group] = [{
                        'id': id,
                        "name": name,
                        "begin": str(begin),
                        "end": str(end),
                        "duration": str(duration),
                        "location": location,
                        "description": description,
                        "prof": prof,
                        "color": str(colors[course]),
                    }]
        else:
            try:
                # if the group is already in the list
                json_list[group].append({
                    'id': id,
                    'name': name,
                    'begin': str(begin),
                    'end': str(end),
                    'duration': str(duration),
                    'location': location,
                    'description': description,
                    'prof': prof,
                    'color': str(colors[course]),
                })
            except:
                # if the group is not in the list
                json_list[group] = [{
                    'id': id,
                    "name": name,
                    "begin": str(begin),
                    "end": str(end),
                    "duration": str(duration),
                    "location": location,
                    "description": description,
                    "prof": prof,
                    "color": str(colors[course]),
                }]
        id += 1
    print("Parsed")

    for group in group_list:
        json_list[group] = sorted(json_list[group], key=lambda k: k['begin'])

    data = json.dumps(json_list, indent=4, sort_keys=True, ensure_ascii=False)

    with open(f"./data/{filename}.json", "w") as file:
        file.write(data)
        print(f"Saved to ./data/{filename}.json")

    with open(f"./data/colors.json", "w") as file:
        file.write(json.dumps(js_colors, indent=4, sort_keys=True, ensure_ascii=False))
        print(f"Saved to ./data/colors.json")

    print("Done")
    time.sleep(1)

get_ics(supported_edt[1]['url'], supported_edt[1]['name'])