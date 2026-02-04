#!/usr/bin/python3
#cabin_search.py

import argparse
import scrape
import report_formatter
from cabin import KeyCabin
from config import REQUIRED_AMENITIES, MIN_OCCUPANCY, MAX_OCCUPANCY, MIN_BEDS, MAX_BEDS, MIN_BATHS, MAX_BATHS, MIN_UP_BEDS


#create tuples with the start and end dates for each weekend in June, july, and august 2026 adding on the friday before and monday after
SUMMER_WEEKENDS_2026 = [
    # June 2026
    # ("June Weekend 1", "06", "05", "2026", "06", "08", "2026"),
    # ("June Weekend 2", "06", "12", "2026", "06", "15", "2026"),
    # ("June Weekend 3", "06", "19", "2026", "06", "22", "2026"),
    # ("June Weekend 4", "06", "26", "2026", "06", "29", "2026"),
    # # July 2026
    # ("July Weekend 1", "07", "03", "2026", "07", "06", "2026"),
    # ("July Weekend 2", "07", "10", "2026", "07", "13", "2026"),
    ("July Weekend 3", "07", "17", "2026", "07", "20", "2026"),
    ("July Weekend 4", "07", "24", "2026", "07", "27", "2026"),
    # August 2026
    # ("August Weekend 1", "07", "31", "2026", "08", "03", "2026"),
    # ("August Weekend 2", "08", "07", "2026", "08", "10", "2026"),
    # ("August Weekend 3", "08", "14", "2026", "08", "17", "2026"),
    # ("August Weekend 4", "08", "21", "2026", "08", "24", "2026"),
    # ("August Weekend 5", "08", "28", "2026", "08", "31", "2026"),
]


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




# Get list of prices by cabin for a specific weekend
def prices_for_cabins_on_weekend(weekend):
    #unpack weekend tuple
    name, bm, bd, by, em, ed, ey = weekend
    print(f"Processing {name}...")
    result = scrape.search(bm, bd, by, em, ed, ey)
    print("Search complete, processing results...")
    cabins = scrape.process_cabin_list(result)

    filtered_cabins = []

    for cabin in cabins:
        if MIN_OCCUPANCY <= cabin.occupancy <= MAX_OCCUPANCY and MIN_BEDS <= cabin.beds <= MAX_BEDS and MIN_BATHS <= cabin.baths <= MAX_BATHS:
            req_amen_names =[amenity.name for amenity in REQUIRED_AMENITIES]
            if set(req_amen_names) > set(cabin.amenities):
                print(f"Missing amenities for {cabin.name}: {set(req_amen_names) - set(cabin.amenities)}")
                continue

            if cabin.up_beds < MIN_UP_BEDS:
                print(f"Not enough upper beds for {cabin.name}: {cabin.up_beds} < {MIN_UP_BEDS}")
                continue
            
            filtered_cabins.append(cabin)

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


def report(cabin_prices_by_weekend: dict[str, list[KeyCabin]], average_prices):
    lines = []
    all_cabins_dict = {}
    for weekend_name, cabins in cabin_prices_by_weekend.items():
        lines.append(f"\nCabin prices for {weekend_name}:")
        for cabin in cabins:
            all_cabins_dict[cabin.name] = cabin
            lines.append(f"  \"{cabin.name}\":")
            lines.append(f"    Price: ${cabin.price:.2f}")
            lines.append(f"    URL: {cabin.url}")
            lines.append(f"    Occupancy: {cabin.occupancy}")
            lines.append(f"    Upper Beds: {cabin.up_beds}")
            lines.append(f"    Main Beds: {cabin.main_beds}")
            lines.append(f"    Lower Beds: {cabin.low_beds}")
            lines.append(f"    Score: {cabin.get_score()}")
            if cabin.gar_beds > 0: lines.append(f"    Garage Beds: {cabin.gar_beds}")
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

        for amenity in [a for a in cabin.amenities if a not in [ra.name for ra in REQUIRED_AMENITIES]]:
            lines.append(f"    - {amenity}")

    if len(scrape.get_cabins_needing_url_names()) > 0:
        lines.append("\nRejected cabins:")
        for cabin_name in scrape.get_cabins_needing_url_names():
            lines.append(f"  - {cabin_name}")

    return "\n".join(lines)


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Search for cabins and generate reports')
    parser.add_argument('--output', '-o', 
                       default='cabin-report.html',
                       help='Output HTML filename (default: cabin-report.html)')
    args = parser.parse_args()
    
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
    
    # Generate HTML report directly from Python data structures
    print("Generating HTML report...")
    months_to_include = {"June", "July", "August"}
    required_amenity_names = [amenity.name for amenity in REQUIRED_AMENITIES]
    data_dict = report_formatter.build_data_from_python(
        cabin_price_list_by_weekend, 
        average_price_of_cabin_by_weekend,
        required_amenity_names
    )
    html_output = report_formatter.format(data_dict, months_to_include)
    with open(args.output, 'w') as f:
        f.write(html_output)
    
    print(f"HTML report generated: {args.output}")


if __name__ == "__main__":
    main()
