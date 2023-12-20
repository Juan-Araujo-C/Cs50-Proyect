import requests
from datetime import datetime
from flask import flash

def get_api_data_for_map():
    EONET_url = 'https://eonet.gsfc.nasa.gov/api/v2.1/events'
    
    # Make a request to NASA's API
    response = requests.get(EONET_url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Limit events to the latest 50
        all_events = response.json().get('events', [])
        latest_events = all_events[:50]

        # Return limited data in JSON format
        return {'events': latest_events}
    else:
        # If the request was unsuccessful, display an error message
        flash("Error fetching data from NASA API", "error")
        return {'events': []}
    

def get_api_data_for_hist(start_index, limit=10):
    EONET_url = 'https://eonet.gsfc.nasa.gov/api/v2.1/events'

    # Make a request to NASA's API
    response = requests.get(EONET_url)

    if response.status_code == 200:
        all_events = response.json().get('events', [])

        # Limit events based on the start index and desired quantity
        start_index = max(0, start_index - 1)  # Adjust the index to 0 if negative
        end_index = start_index + limit
        limited_events = all_events[start_index:end_index]

        return {'events': limited_events, 'total_count': len(all_events)}
    else:
        flash("Error fetching data from NASA API", "error")
        return {'events': [], 'total_count': 0}


def format_date(date_string):
    try:
        date_object = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
        formatted_date = date_object.strftime("%Y-%m-%d")
        return formatted_date
    except ValueError:
        return "Invalid Date"