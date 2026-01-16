#!/usr/bin/python3
#railey_scraper.py

import requests
import json
from cabin import Cabin, KeyCabin
from bs4 import BeautifulSoup
import threading
import copy
import re

SEARCH_URL = "https://www.deepcreek.com/rcapi/item/avail/search?rcav%5Bbegin%5D={0}%2F{1}%2F{2}&rcav%5Bend%5D={3}%2F{4}%2F{5}&rcav%5Badult%5D=1&rcav%5Bchild%5D=0&rcav%5Bflex%5D=&rcav%5Bflex_type%5D=d"

BEDS = ".rc-lodging-beds"
BATHS = ".rc-lodging-baths"
OCCUPANCY = ".rc-lodging-occ"

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

cabins_needing_url_names = []

MIN_OCCUPANCY = 13
MAX_OCCUPANCY = 18
MIN_BEDS = 4
MAX_BEDS = 16
MIN_BATHS = 3
MAX_BATHS = 14

REQUIRED_AMENITIES = ["Grills (Gas)", "A/C: Central Air", "WIFI", "Outdoor Fire Pit"]
OPTIONAL_AMENITIES = ["Swimming Pool (Community)", "Swimming Pool (Private)", "CARC", "Pool Table", "Home Theater"]

cabin_key_details_dict = {}

#create tuples with the start and end dates for each weekend in June, july, and august 2026 adding on the friday before and monday after
SUMMER_WEEKENDS_2026 = [
    # June 2026
    ("June Weekend 1", "06", "05", "2026", "06", "08", "2026"),
    ("June Weekend 2", "06", "12", "2026", "06", "15", "2026"),
    ("June Weekend 3", "06", "19", "2026", "06", "22", "2026"),
    ("June Weekend 4", "06", "26", "2026", "06", "29", "2026"),
    # July 2026
    ("July Weekend 1", "07", "03", "2026", "07", "06", "2026"),
    ("July Weekend 2", "07", "10", "2026", "07", "13", "2026"),
    ("July Weekend 3", "07", "17", "2026", "07", "20", "2026"),
    ("July Weekend 4", "07", "24", "2026", "07", "27", "2026"),
    # August 2026
    ("August Weekend 1", "07", "31", "2026", "08", "03", "2026"),
    ("August Weekend 2", "08", "07", "2026", "08", "10", "2026"),
    ("August Weekend 3", "08", "14", "2026", "08", "17", "2026"),
    ("August Weekend 4", "08", "21", "2026", "08", "24", "2026"),
    ("August Weekend 5", "08", "28", "2026", "08", "31", "2026"),
]


def search(bm, bd, by, em, ed, ey):
    response = requests.get(SEARCH_URL.format(bm, bd, by, em, ed, ey))
    return response.content

def get_average_price(cabins):
    total_price = 0
    count = 0
    for cabin in cabins:
        price = cabin.get_price()
        if price is not None:
            total_price += price
            count += 1
    if count == 0:
        return None
    return total_price / count

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
            if found_amenity.find(string=re.compile(re.escape(desired_amenity))):
                available_amenity_list.append(desired_amenity)
                # print(f"Found {desired_amenity} at {name}")

    beds_text = soup.select_one(BEDS).text.strip() if soup.select_one(BEDS) else "N/A"
    beds = ''.join(filter(str.isdigit, beds_text)) if beds_text != "N/A" else "N/A"
    if beds_text == "N/A":
        cabins_needing_url_names.append(name)
    
    baths_text = soup.select_one(BATHS).text.strip() if soup.select_one(BATHS) else "N/A"
    baths = ''.join(filter(str.isdigit, baths_text)) if baths_text != "N/A" else "N/A"
    
    occupancy_text = soup.select_one(OCCUPANCY).text.strip() if soup.select_one(OCCUPANCY) else "N/A"
    occupancy = ''.join(filter(str.isdigit, occupancy_text)) if occupancy_text != "N/A" else "N/A"
    
    return KeyCabin(name=name, occupancy=int(occupancy) if occupancy != "N/A" else 0, beds=int(beds) if beds != "N/A" else 0, baths=int(baths) if baths != "N/A" else 0, url=cabin_url,amenities=available_amenity_list)



# Get list of prices by cabin for a specific weekend
def prices_for_cabins_on_weekend(weekend):
    #unpack weekend tuple
    name, bm, bd, by, em, ed, ey = weekend
    print(f"Processing {name}...")
    result = search(bm, bd, by, em, ed, ey)
    print("Search complete, processing results...")
    cabins = process_cabin_list(result)

    filtered_cabins = [
        cabin for cabin in cabins
        if MIN_OCCUPANCY <= cabin.occupancy <= MAX_OCCUPANCY
        and MIN_BEDS <= cabin.beds <= MAX_BEDS
        and MIN_BATHS <= cabin.baths <= MAX_BATHS
        and set(REQUIRED_AMENITIES) <= set(cabin.amenities)
    ]

    # Apply filters based on occupancy, beds, and baths
    return filtered_cabins

def average_prices_for_weekends(cabin_prices_by_weekend):
    average_prices = {}
    for weekend_name in cabin_prices_by_weekend.keys():
        avg_price = get_average_price(cabin_prices_by_weekend[weekend_name])
        average_prices[weekend_name] = avg_price
    
    return average_prices

def least_expensive_weekend(average_prices):
    return min(average_prices.items(), key=lambda x: x[1] if x[1] is not None else float('inf'))


def report(cabin_prices_by_weekend, average_prices):
    lines = []
    all_cabins_dict = {}
    for weekend_name, cabins in cabin_prices_by_weekend.items():
        lines.append(f"\nCabin prices for {weekend_name}:")
        for cabin in cabins:
            all_cabins_dict[cabin.name] = cabin
            lines.append(f"  \"{cabin.name}\":")
            lines.append(f"    Price: ${cabin.price:.2f}")
            lines.append(f"    URL: {cabin.url}")
        avg_price = average_prices[weekend_name]
        if avg_price is not None:
            lines.append(f"Average price for {weekend_name}: ${avg_price:.2f}")
        else:
            lines.append(f"No cabins available for {weekend_name}.")
    
    cheapest_weekend, cheapest_price = least_expensive_weekend(average_prices)
    if cheapest_price is not None:
        lines.append(f"\nLeast Expensive Weekend: {cheapest_weekend}\nAverage Price: ${cheapest_price:.2f}")
    else:
        lines.append("\nNo weekends have available cabins.")

    # for each cabin in the all-cabins dict
    lines.append(f"\nCabin amenities:")
    for cabin in all_cabins_dict.values():
        #add lines for the optional amenities
        lines.append(f"  {cabin.name}:")

        for amenity in [a for a in cabin.amenities if a not in REQUIRED_AMENITIES]:
            lines.append(f"    - {amenity}")

    if len(cabins_needing_url_names) > 0:
        lines.append("\nRejected cabins:")
        for cabin_name in cabins_needing_url_names:
            lines.append(f"  - {cabin_name}")

    return "\n".join(lines)


def main():
    print("Begin scraping of Railey Cabins for Syndicate")
    cabin_price_list_by_weekend = {}
    for weekend in SUMMER_WEEKENDS_2026:
        cabins = prices_for_cabins_on_weekend(weekend)
        name = weekend[0]
        cabin_price_list_by_weekend[name] = cabins
        

    average_price_of_cabin_by_weekend = average_prices_for_weekends(cabin_price_list_by_weekend)
    cabin_report = report(cabin_price_list_by_weekend, average_price_of_cabin_by_weekend)
    with open('cabin-report.yml', 'w') as f:
        f.write(cabin_report)
    
    print("Scraping complete. Report written to cabin-report.yml")


if __name__ == "__main__":
    main()