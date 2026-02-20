from amenity import Amenity

MIN_OCCUPANCY = 13
MAX_OCCUPANCY = 15
MIN_BEDS = 4
MAX_BEDS = 16
MIN_BATHS = 4
MAX_BATHS = 14

MIN_UP_BEDS = 2
MIN_UP_PLUS_MAIN_BEDS = 4

REQUIRED_AMENITIES = [
    Amenity("Grill", ["Grills (Gas)"]), 
    Amenity("A/C",["A/C: Central Air"]), 
    Amenity("Wifi", ["Internet: Wifi" , "Internet: Mesh WIFI System"]), 
    Amenity("Fire Pit", ["Outdoor Fire Pit"])
]
OPTIONAL_AMENITIES = [
    Amenity("Pool", ["Swimming Pool (Community)", "Swimming Pool (Private)", "CARC"]), 
    Amenity("Pool Table", ["Pool Table"]), 
    Amenity("Home Theater", ["Home Theater"])
] 
