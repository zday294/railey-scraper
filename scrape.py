#scrape.py
import threading
import requests
import json
import copy
import re
from bs4 import BeautifulSoup
from cabin import KeyCabin, Cabin
from config import REQUIRED_AMENITIES, OPTIONAL_AMENITIES

SEARCH_URL = "https://www.deepcreek.com/rcapi/item/avail/search?rcav%5Bbegin%5D={0}%2F{1}%2F{2}&rcav%5Bend%5D={3}%2F{4}%2F{5}&rcav%5Badult%5D=1&rcav%5Bchild%5D=0&rcav%5Bflex%5D=&rcav%5Bflex_type%5D=d"

BEDS = ".rc-lodging-beds"
BATHS = ".rc-lodging-baths"
OCCUPANCY = ".rc-lodging-occ"

UPPER_BEDS = "Upper Level: Bedroom"
MAIN_BEDS = "Main Level: Bedroom"
LOWER_BEDS = "Lower Level: Bedroom"
ABOVE_GARAGE_BEDS = "Above Garage: Bedroom"

CABIN_URL_NAMES = {
    "All In": "all",
    "Almost Heaven": "almost-heaven-0",
    "A-Frame of Mind": "frame-mind",
    "Bear Run Lodge": "bear-run-lodge-0",
    "Fireside Lodge": "fireside-lodge-0",
    "Get Your Creek On": "get-your-creek",
    "Into The Woods" : "woods",
    "Knotty -N- Nice": "knotty-n-nice",
    "Lake Escape": "lake-escape-0",
    "On The Rocks": "rocks",
    "Pop-a-Top Inn": "pop-top-inn",
    "The O A Chalet": "o-chalet",
    "Tips Up": "tips",
}

cabin_key_details_dict = {}
cabins_needing_url_names = []

def dash_replace(name: str, phrase: str):
    if phrase in name:
        return name.replace(phrase, "-")
    else:
        return name


def name_to_url_name(name: str):
    url_name = ""

    if "A " == name[:2]:
        url_name = name.replace("A ", "", 1).lower()
    elif "The " == name[:4]:
        url_name = name.replace("The ", "", 1).lower()
    elif "At " == name[:3]:
        url_name = name.replace("At ", "", 1).lower()
    elif "On " == name[:3]:
        url_name = name.replace("On ", "", 1).lower()
    elif "Up The " == name[:7]:
        url_name = name.replace("Up The ", "", 1).lower()
    else: 
        url_name = name.lower()

    for phr in [" - ", " is on ", " of the ", " on the ", " at the ", " by the ", " of a ", " off the ", " in the ", " to ", " the ", " of ", " on ", " in ", " at ", " from ", " up ", " by "]:
        url_name = dash_replace(url_name, phr)

    if " & " in url_name:
        url_name = url_name.replace(" & ", "-")
    elif "&" in url_name:
        url_name = url_name.replace("&", "-")

    url_name = url_name.replace("....", "").replace("'","").replace(",","").replace("!", "").replace("#", "").replace("(", "").replace(")","").replace(".","").replace(" ", "-")

    return url_name

def get_key_cabin_details(name: str) -> KeyCabin:
    name_url = CABIN_URL_NAMES[name] if name in CABIN_URL_NAMES.keys() else name_to_url_name(name)
    cabin_url = f"https://www.deepcreek.com/vacation-rentals/{name_url}"
    print(f"Scraping details for cabin: {name} @ {cabin_url}")
    result = requests.get(cabin_url)
    soup = BeautifulSoup(result.content, "html.parser")

    # add all amenities here
    full_amenity_list = REQUIRED_AMENITIES + OPTIONAL_AMENITIES
    available_amenity_list = []

    for found_amenity in soup.find_all(name="li", class_="amenity-list-item"):
        for desired_amenity in full_amenity_list:
            for amenity_key in desired_amenity.keys:
                if found_amenity.find(string=re.compile(re.escape(amenity_key))):
                    available_amenity_list.append(desired_amenity.name)
                    break
    up_beds = soup.find_all(string=re.compile(UPPER_BEDS))
    low_beds = soup.find_all(string=re.compile(LOWER_BEDS))
    main_beds = soup.find_all(string=re.compile(MAIN_BEDS))
    ab_g_beds = soup.find_all(string=re.compile(ABOVE_GARAGE_BEDS))
    

    beds_text = soup.select_one(BEDS).text.strip() if soup.select_one(BEDS) else "N/A"
    beds = ''.join(filter(str.isdigit, beds_text)) if beds_text != "N/A" else "N/A"
    if beds_text == "N/A":
        cabins_needing_url_names.append(name)
    
    baths_text = soup.select_one(BATHS).text.strip() if soup.select_one(BATHS) else "N/A"
    baths = ''.join(filter(str.isdigit, baths_text)) if baths_text != "N/A" else "N/A"
    
    occupancy_text = soup.select_one(OCCUPANCY).text.strip() if soup.select_one(OCCUPANCY) else "N/A"
    occupancy = ''.join(filter(str.isdigit, occupancy_text)) if occupancy_text != "N/A" else "N/A"
    
    return KeyCabin(
        name=name, 
        occupancy=int(occupancy) if occupancy != "N/A" else 0, 
        beds=int(beds) if beds != "N/A" else 0, 
        up_beds=len(up_beds),
        main_beds=len(main_beds),
        low_beds=len(low_beds),
        gar_beds=len(ab_g_beds),
        baths=int(baths) if baths != "N/A" else 0, 
        url=cabin_url,
        amenities=available_amenity_list
    )

def search(bm, bd, by, em, ed, ey):
    response = requests.get(SEARCH_URL.format(bm, bd, by, em, ed, ey))
    return response.content

def cabin_detail_thread(cabin_name, cabin_price, cabins_list):
    key_cabin = get_key_cabin_details(cabin_name)
    cabin_key_details_dict[cabin_name] = copy.deepcopy(key_cabin)
    key_cabin.price = cabin_price
    cabins_list.append(key_cabin)

def process_cabin_list(json_data) -> list[KeyCabin]:
    railey_cabins = [Cabin.from_dict(item) for item in json.loads(json_data)]

    key_cabins = []
    threads = []
    for cabin in railey_cabins:
        if cabin.name in cabin_key_details_dict.keys():
            key_inst = copy.deepcopy(cabin_key_details_dict[cabin.name])
            key_inst.price = cabin.get_price()
            key_cabins.append(key_inst)
        else:
            thread = threading.Thread(target=cabin_detail_thread, args=(cabin.name, cabin.get_price(), key_cabins))
            thread.start()
            threads.append(thread)

    for thread in threads:
        thread.join()

    return key_cabins