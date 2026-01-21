#!/usr/bin/python3
#future-costs.py

import scrape
import statistics
from cabin import KeyCabin

# WEEKEND = ("July Weekend 3", "07", "17", "2026", "07", "20", "2026")

def averge_cabin_price(cabins: list[KeyCabin], occupancy: int) -> float:
    return statistics.mean([cabin.price for cabin in cabins if cabin.occupancy == occupancy])


def main():
    print("Obtaiing costs")
    res = scrape.search("07", "17", "2026", "07", "20", "2026")
    cabins = scrape.process_cabin_list(res)

    print(f"2026 occupancy average price = {averge_cabin_price(cabins, 13)}")
    print(f"2027 occupancy average price = {averge_cabin_price(cabins, 15)}")
    print(f"2029 occupancy average price = {averge_cabin_price(cabins, 16)}")
    print(f"2030 occupancy average price = {averge_cabin_price(cabins, 17)}")

if __name__ == "__main__":
    main()