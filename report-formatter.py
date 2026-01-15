#!/usr/bin/python3
#report-formatter.py

import yaml
from typing import Dict, List, Set
import statistics
from datetime import datetime

def parse_cabin_data(filepath: str) -> Dict:
    """Load and parse the YAML cabin report file."""
    with open(filepath, 'r') as f:
        data = yaml.safe_load(f)
    return data

def extract_cabin_prices(data: Dict, months_to_include: Set[str]) -> Dict[str, Dict[str, Dict]]:
    """Extract cabin prices and URLs organized by cabin name and weekend."""
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
                if isinstance(price_str, str) and price_str.startswith('$'):
                    price_value = float(price_str.replace('$', '').replace(',', ''))
                    if cabin not in cabin_data:
                        cabin_data[cabin] = {'prices': {}, 'url': url}
                    cabin_data[cabin]['prices'][weekend_name] = price_value
                    # Use the URL from any weekend (they should be the same)
                    if not cabin_data[cabin]['url']:
                        cabin_data[cabin]['url'] = url
    
    return cabin_data

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

def generate_html_table(cabin_data: Dict[str, Dict[str, Dict]], months_to_include: Set[str] = None) -> str:
    """Generate HTML table with highlighted best prices and hyperlinked cabin names."""
    
    # Get all weekends (columns) and sort them
    all_weekends = set(
        weekend for cabin_info in cabin_data.values() 
        for weekend in cabin_info['prices'].keys()
    )
    all_weekends = sort_weekends(list(all_weekends))
    
    # Get all cabins (rows)
    all_cabins = sorted(cabin_data.keys())
    
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
    </style>
</head>
<body>
    <h1>Cabin Pricing Report</h1>
"""
    
    if months_to_include:
        html += f"    <p>Showing data for: {', '.join(sorted(months_to_include))}</p>\n"
    
    html += """    <table>
        <thead>
            <tr>
                <th>Cabin</th>
"""
    
    for weekend in all_weekends:
        html += f"                <th>{weekend}</th>\n"
    
    html += """                <th>Average Price</th>
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
        
        # Find minimum price for this cabin
        prices = list(cabin_data[cabin]['prices'].values())
        min_price = min(prices) if prices else None
        avg_price = statistics.mean(prices) if prices else 0
        
        for weekend in all_weekends:
            if weekend in cabin_data[cabin]['prices']:
                price = cabin_data[cabin]['prices'][weekend]
                is_best = (price == min_price)
                price_class = "best-price" if is_best else "available"
                html += f"                <td class='{price_class}'>${price:,.2f}</td>\n"
            else:
                html += "                <td class='unavailable'>—</td>\n"
        
        html += f"                <td><strong>${avg_price:,.2f}</strong></td>\n"
        html += "            </tr>\n"
    
    html += """        </tbody>
    </table>
</body>
</html>
"""
    
    return html

def main():
    # Configuration: specify which months to include (None = all months)
    # Options: "June", "July", "August"
    months_to_include = {"June", "July", "August"}  # or None for all months
    
    # Load and process data
    data = parse_cabin_data('cabin-report.yml')
    cabin_data = extract_cabin_prices(data, months_to_include)
    
    # Generate HTML
    html_output = generate_html_table(cabin_data, months_to_include)
    
    # Save to file
    with open('cabin-report.html', 'w') as f:
        f.write(html_output)
    
    print("HTML report generated: cabin-report.html")

if __name__ == "__main__":
    main()