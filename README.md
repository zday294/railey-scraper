# Railey Scraper

This pair of Python scripts creates an html document with a report of all the cabin prices from Railey Real Estate for each weekend in June, July, and August. Cabins displayed all have an occupancy between 13 and 18, at least 4 beds, and at least 3 baths. Additionally, gas grills, central A/C, Wi-Fi, and an outdoor fire pit are included as required amenities. Looking to add ways to make note of optional amenities like a pool

## Necessary Dependencies
- Python (obviously) - 3.14 used for this project
- pyyaml
- bs4 (aka BeautifulSoup)
- requests

## How to run

Once dependencies are installed simply run `python scrape.py` followed by `python report-formmater.py`. The combo of these two commands will create an html doc with a report of all the cabin prices for the weekends included in the code, as well as reporting which optional amenities are included and giving a score for each cabin based on the included features. 

## Changing parameter values

`config.py` contains the following configurable parameters 
- MIN_OCCUPANCY / MAX_OCCUPANCY - Cabins with an occupancy that is at least (>=) MIN_OCCUPANCY and at most (<=) MAX_OCCUPANCY will be included in the results
- MIN_BEDS / MAX_BEDS - Cabins with a number of bedrooms equal to at least MIN_BEDS and at most MAX_BEDS
- MIN_BATHS / MAX_BATHS - Cabins with a number of bathrooms equal to at least MIN_BATHS and at most MAX_BATHS
- MIN_UP_BEDS - The minimum number of bedrooms on a floor above the main floor. 
- REQUIRED_AMENITIES - The amenities that a cabin must have to be included in the list. This is a list of `Amentiy` objects defined in `amenity.py`.
- OPTIONAL_AMENITIES - Amenities that would be nice to have but are not necessary to consider a cabin. Also a list of `Amenity` objects.  


## AI Disclosure

This project has been created partly through the use of generative AI tools, specifically GitHub Copilot. `report-formatter.py` has been written and updated by assigning tasks to an AI agent.