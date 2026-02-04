# Railey Scraper

This pair of Python scripts creates an html document with a report of all the cabin prices from Railey Real Estate for each weekend in June, July, and August. Cabins displayed all have an occupancy between 13 and 18, at least 4 beds, and at least 3 baths. Additionally, gas grills, central A/C, Wi-Fi, and an outdoor fire pit are included as required amenities. Looking to add ways to make note of optional amenities like a pool

## Necessary Dependencies
- Python (obviously) - 3.14 used for this project
- pyyaml
- bs4 (aka BeautifulSoup)
- requests

## How to run

Once dependencies are installed simply run `python scrape.py` followed by `python report-formmater.py`. The combo of these two commands will create an html doc with a report of all the cabin prices for 

## Changing parameter values

`config.py` contains the following configurable parameters 
- MIN_OCCUPANCY / MAX_OCCUPANCY - Cabins with an occupancy that is at least (>=) MIN_OCCUPANCY and at most (<=) MAX_OCCUPANCY will be included in the results
- MIN_BEDS / MAX_BEDS - Cabins with at least a  MIN_BEDS and 


## AI Disclosure

This project has been created partly through the use of generative AI tools, specifically GitHub Copilot. `report-formatter.py` has been written and updated by assigning tasks to an AI agent.