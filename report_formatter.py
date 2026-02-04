#!/usr/bin/python3
#report-formatter.py

import yaml
import argparse
from typing import Dict, List, Set
import statistics
from datetime import datetime


def parse_cabin_data(yaml_string: str) -> Dict:
    """Parse YAML cabin report from a string."""
    data = yaml.safe_load(yaml_string)
    return data

def build_data_from_python(cabin_prices_by_weekend: Dict, average_prices: Dict, required_amenities: List = None) -> Dict:
    """Build the data structure directly from Python objects (KeyCabin instances).
    
    Args:
        cabin_prices_by_weekend: Dict mapping weekend names to lists of KeyCabin objects
        average_prices: Dict mapping weekend names to average prices
        required_amenities: List of required amenity names to filter out from display
        
    Returns:
        Dict in the same format as YAML-parsed data
    """
    if required_amenities is None:
        required_amenities = []
    
    data = {}
    all_cabins_dict = {}
    
    # Build cabin prices by weekend
    for weekend_name, cabins in cabin_prices_by_weekend.items():
        weekend_key = f"Cabin prices for {weekend_name}"
        data[weekend_key] = {}
        
        for cabin in cabins:
            all_cabins_dict[cabin.name] = cabin
            cabin_info = {
                'Price': f'${cabin.price:.2f}',
                'URL': cabin.url,
                'Occupancy': cabin.occupancy,
                'Upper Beds': cabin.up_beds,
                'Main Beds': cabin.main_beds,
                'Lower Beds': cabin.low_beds,
                'Score': cabin.get_score()
            }
            if cabin.gar_beds > 0:
                cabin_info['Garage Beds'] = cabin.gar_beds
            
            data[weekend_key][cabin.name] = cabin_info
        
        # Add average price for this weekend
        avg_price = average_prices.get(weekend_name)
        if avg_price is not None:
            data[f"Average price for {weekend_name}"] = f'${avg_price:.2f}'
    
    # Build amenities section (excluding required amenities)
    data['Cabin amenities'] = {}
    for cabin in all_cabins_dict.values():
        optional_amenities = [a for a in cabin.amenities if a not in required_amenities]
        if optional_amenities:
            data['Cabin amenities'][cabin.name] = optional_amenities
        else:
            data['Cabin amenities'][cabin.name] = None
    
    return data

def extract_cabin_prices(data: Dict, months_to_include: Set[str]) -> Dict[str, Dict[str, Dict]]:
    """Extract cabin prices, URLs, and bed information organized by cabin name and weekend."""
    cabin_data = {}
    
    for weekend_key, weekend_data in data.items():
        if not isinstance(weekend_data, dict):
            continue
            
        # Extract month from weekend key (e.g., "Cabin prices for June Weekend 1")
        parts = weekend_key.split()
        if len(parts) >= 4:
            month = parts[3]
            if months_to_include and month not in months_to_include:
                continue
        
        weekend_name = ' '.join(parts[3:])  # "June Weekend 1"
        
        for cabin, cabin_info in weekend_data.items():
            if isinstance(cabin_info, dict) and 'Price' in cabin_info:
                price_str = cabin_info['Price']
                url = cabin_info.get('URL', '')
                upper_beds = cabin_info.get('Upper Beds', 0)
                main_beds = cabin_info.get('Main Beds', 0)
                lower_beds = cabin_info.get('Lower Beds', 0)
                garage_beds = cabin_info.get('Garage Beds', 0)
                occupancy = cabin_info.get('Occupancy', 0)
                score = cabin_info.get('Score', 0)
                
                if isinstance(price_str, str) and price_str.startswith('$'):
                    price_value = float(price_str.replace('$', '').replace(',', ''))
                    if cabin not in cabin_data:
                        cabin_data[cabin] = {
                            'prices': {}, 
                            'scores': {},
                            'url': url,
                            'upper_beds': upper_beds,
                            'main_beds': main_beds,
                            'lower_beds': lower_beds,
                            'garage_beds': garage_beds,
                            'occupancy': occupancy
                        }
                    cabin_data[cabin]['prices'][weekend_name] = price_value
                    cabin_data[cabin]['scores'][weekend_name] = score
                    # Use the URL from any weekend (they should be the same)
                    if not cabin_data[cabin]['url']:
                        cabin_data[cabin]['url'] = url
    
    return cabin_data

def extract_amenities(data: Dict) -> Dict[str, Set[str]]:
    """Extract cabin amenities from YAML data."""
    cabin_amenities = {}
    
    if 'Cabin amenities' in data:
        amenities_section = data['Cabin amenities']
        if isinstance(amenities_section, dict):
            for cabin, amenities_list in amenities_section.items():
                if amenities_list is None:
                    cabin_amenities[cabin] = set()
                elif isinstance(amenities_list, list):
                    # Remove duplicates by converting to set
                    cabin_amenities[cabin] = set(amenities_list)
                else:
                    cabin_amenities[cabin] = set()
    
    return cabin_amenities

def get_all_amenities(cabin_amenities: Dict[str, Set[str]]) -> List[str]:
    """Get sorted list of all unique amenities."""
    all_amenities = set()
    for amenities in cabin_amenities.values():
        all_amenities.update(amenities)
    return sorted(all_amenities)

def extract_weekend_averages(data: Dict) -> Dict[str, float]:
    """Extract weekend average prices from YAML data."""
    weekend_averages = {}
    
    for key, value in data.items():
        if key.startswith('Average price for '):
            # Extract weekend name from "Average price for June Weekend 1"
            weekend_name = key.replace('Average price for ', '')
            if isinstance(value, str) and value.startswith('$'):
                try:
                    price = float(value.replace('$', '').replace(',', ''))
                    weekend_averages[weekend_name] = price
                except ValueError:
                    continue
    
    return weekend_averages

def get_orange_saturation(price: float, min_price: float, max_price: float) -> str:
    """Calculate orange color saturation based on price relative to min/max range."""
    if max_price == min_price:
        return "rgba(255, 152, 0, 0.8)"  # Default orange if no range
    
    # Normalize price to 0-1 range
    normalized = (price - min_price) / (max_price - min_price)
    
    # Map to saturation range (0.3 to 1.0 for visibility)
    saturation = 0.3 + (normalized * 0.7)
    
    return f"rgba(255, 152, 0, {saturation:.2f})"

def sort_weekends(weekends: List[str]) -> List[str]:
    """Sort weekends by month order, then by weekend number."""
    month_order = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4,
        'May': 5, 'June': 6, 'July': 7, 'August': 8,
        'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    
    def weekend_sort_key(weekend_str):
        parts = weekend_str.split()
        month = parts[0]
        weekend_num = int(parts[2]) if len(parts) >= 3 and parts[2].isdigit() else 0
        return (month_order.get(month, 99), weekend_num)
    
    return sorted(weekends, key=weekend_sort_key)

def generate_html_table(cabin_data: Dict[str, Dict[str, Dict]], cabin_amenities: Dict[str, Set[str]], data: Dict, months_to_include: Set[str] = None) -> str:
    """Generate HTML table with highlighted best prices, hyperlinked cabin names, and amenity columns."""
    
    # Get all weekends (columns) and sort them
    all_weekends = set(
        weekend for cabin_info in cabin_data.values() 
        for weekend in cabin_info['prices'].keys()
    )
    all_weekends = sort_weekends(list(all_weekends))
    
    # Get all cabins (rows)
    all_cabins = sorted(cabin_data.keys())
    
    # Get all amenities (columns)
    all_amenities = get_all_amenities(cabin_amenities)
    
    html = """<!DOCTYPE html>
<html>
<head>
    <style>
        table {
            border-collapse: collapse;
            font-family: Arial, sans-serif;
            margin: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
        }
        th {
            background-color: #4CAF50;
            color: white;
        }
        .cabin-name {
            font-weight: bold;
            text-align: left;
            background-color: #f2f2f2;
        }
        .cabin-name a {
            color: #2c5aa0;
            text-decoration: none;
        }
        .cabin-name a:hover {
            text-decoration: underline;
        }
        .best-price {
            background-color: #00C853;
            color: white;
            font-weight: bold;
        }
        .available {
            background-color: #C8E6C9;
        }
        .unavailable {
            background-color: #ffebee;
            color: #999;
        }
        .amenity-header {
            background-color: #2196F3;
            color: white;
        }
        .has-amenity {
            background-color: #E3F2FD;
            font-weight: bold;
        }
        .no-amenity {
            background-color: #f5f5f5;
            color: #ccc;
        }
        .bed-header {
            background-color: #9C27B0;
            color: white;
        }
        .bed-info {
            background-color: #F3E5F5;
            text-align: center;
        }
        .weekend-average {
            background-color: #FF9800;
            color: white;
            font-weight: bold;
        }
        .average-row {
            background-color: #FFF3E0;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <h1>Cabin Pricing Report</h1>
"""
    
    if months_to_include:
        html += f"    <p>Showing data for: {', '.join(months_to_include)}</p>\n"
    html += "    <p>Weekend = Friday night to Monday morning</p>"
    html += "    <p>All cabins here incldue a gas grill, Wi-Fi, central air conditioning, and an outdoor firepit.</p>"
    html += "    <p>CARC = Community Aquatic Recreation Center (aka pool)</p>"
    
    html += """    <table>
        <thead>
            <tr>
                <th>Cabin</th>
"""
    
    # Add amenity column headers right after Cabin
    for amenity in all_amenities:
        html += f"                <th class='amenity-header'>{amenity}</th>\n"
    
    # Add bed column headers
    html += "                <th class='bed-header'>Upper Beds</th>\n"
    html += "                <th class='bed-header'>Main Beds</th>\n"
    html += "                <th class='bed-header'>Lower Beds</th>\n"
    html += "                <th class='bed-header'>Garage Beds</th>\n"
    html += "                <th class='bed-header'>Total Beds</th>\n"
    html += "                <th class='bed-header'>Occupancy</th>\n"
    
    for weekend in all_weekends:
        html += f"                <th>{weekend}</th>\n"
    
    html += """                <th>Average Price</th>
                <th>Score</th>
            </tr>
        </thead>
        <tbody>
"""
    
    for cabin in all_cabins:
        html += "            <tr>\n"
        
        # Create hyperlinked cabin name
        cabin_url = cabin_data[cabin].get('url', '')
        if cabin_url:
            html += f"                <td class='cabin-name'><a href='{cabin_url}' target='_blank'>{cabin}</a></td>\n"
        else:
            html += f"                <td class='cabin-name'>{cabin}</td>\n"
        
        # Add amenity cells right after cabin name
        cabin_amenity_set = cabin_amenities.get(cabin, set())
        for amenity in all_amenities:
            if amenity in cabin_amenity_set:
                html += f"                <td class='has-amenity'>✓</td>\n"
            else:
                html += f"                <td class='no-amenity'>—</td>\n"
        
        # Add bed information cells
        upper_beds = cabin_data[cabin].get('upper_beds', 0)
        main_beds = cabin_data[cabin].get('main_beds', 0)
        lower_beds = cabin_data[cabin].get('lower_beds', 0)
        garage_beds = cabin_data[cabin].get('garage_beds', 0)
        total_beds = upper_beds + main_beds + lower_beds + garage_beds
        occupancy = cabin_data[cabin].get('occupancy', 0)
        
        html += f"                <td class='bed-info'>{upper_beds}</td>\n"
        html += f"                <td class='bed-info'>{main_beds}</td>\n"
        html += f"                <td class='bed-info'>{lower_beds}</td>\n"
        html += f"                <td class='bed-info'>{garage_beds if garage_beds > 0 else '—'}</td>\n"
        html += f"                <td class='bed-info'><strong>{total_beds}</strong></td>\n"
        html += f"                <td class='bed-info'><strong>{occupancy}</strong></td>\n"
        
        # Find minimum price for this cabin
        prices = list(cabin_data[cabin]['prices'].values())
        min_price = min(prices) if prices else None
        avg_price = statistics.mean(prices) if prices else 0
        
        # Calculate average score for this cabin
        scores = list(cabin_data[cabin]['scores'].values())
        avg_score = statistics.mean(scores) if scores else 0
        
        for weekend in all_weekends:
            if weekend in cabin_data[cabin]['prices']:
                price = cabin_data[cabin]['prices'][weekend]
                is_best = (price == min_price)
                price_class = "best-price" if is_best else "available"
                html += f"                <td class='{price_class}'>${price:,.2f}</td>\n"
            else:
                html += "                <td class='unavailable'>—</td>\n"
        
        html += f"                <td><strong>${avg_price:,.2f}</strong></td>\n"
        html += f"                <td><strong>{avg_score:,.0f}</strong></td>\n"
        html += "            </tr>\n"
    
    # Get weekend averages from YAML data
    weekend_averages_data = extract_weekend_averages(data)
    
    # Add weekend averages row if we have data
    if weekend_averages_data:
        html += "            <tr class='average-row'>\n"
        html += "                <td class='cabin-name'>Weekend Average</td>\n"
        
        # Add empty cells for amenity columns
        for amenity in all_amenities:
            html += "                <td>—</td>\n"
        
        # Add empty cells for bed columns
        html += "                <td>—</td>\n"  # Upper Beds
        html += "                <td>—</td>\n"  # Main Beds
        html += "                <td>—</td>\n"  # Lower Beds
        html += "                <td>—</td>\n"  # Garage Beds
        html += "                <td>—</td>\n"  # Total Beds
        html += "                <td>—</td>\n"  # Occupancy
        
        # Get price range for color saturation
        available_prices = [weekend_averages_data.get(weekend, 0) for weekend in all_weekends if weekend in weekend_averages_data]
        min_price = min(available_prices) if available_prices else 0
        max_price = max(available_prices) if available_prices else 0
        
        # Add weekend average prices with dynamic coloring
        for weekend in all_weekends:
            if weekend in weekend_averages_data:
                avg_price = weekend_averages_data[weekend]
                color = get_orange_saturation(avg_price, min_price, max_price)
                html += f"                <td style='background-color: {color}; color: white; font-weight: bold;'>${avg_price:,.2f}</td>\n"
            else:
                html += "                <td class='unavailable'>—</td>\n"
        
        # Leave final columns blank as requested
        html += "                <td>—</td>\n"  # Average Price
        html += "                <td>—</td>\n"  # Average Score
        html += "            </tr>\n"
    
    html += """        </tbody>
    </table>
</body>
</html>
"""
    
    return html

def format(yaml_data, months_to_include: Set[str] = None) -> str:
    """Format the given cabin data into an HTML report.
    
    Args:
        yaml_data: Either a YAML string or a dict (already parsed)
        months_to_include: Set of month names to include in the report
        
    Returns:
        HTML string
    """
    if isinstance(yaml_data, str):
        data = parse_cabin_data(yaml_data)
    else:
        # Assume it's already a dict
        data = yaml_data
    
    cabin_data = extract_cabin_prices(data, months_to_include)
    cabin_amenities = extract_amenities(data)
    html_output = generate_html_table(cabin_data, cabin_amenities, data, months_to_include)
    return html_output

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate HTML cabin pricing report')
    parser.add_argument('--output', '-o', 
                       default='cabin-report.html',
                       help='Output HTML filename (default: cabin-report.html)')
    args = parser.parse_args()
    
    # Configuration: specify which months to include (None = all months)
    # Options: "June", "July", "August"
    months_to_include = {"June", "July", "August"}  # or None for all months
    
    # Load and process data
    data = None
    with open('cabin-report.yml', 'r') as f:
        data = yaml.safe_load(f)
    
    # Generate HTML
    html_output = format(yaml_data=data, months_to_include=months_to_include)
    
    # Save to file
    with open(args.output, 'w') as f:
        f.write(html_output)
    
    print(f"HTML report generated: {args.output}")

if __name__ == "__main__":
    main()