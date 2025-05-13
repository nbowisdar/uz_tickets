def convert_booking_url_to_api_url(booking_url: str) -> str:
    """
    Convert a booking.uz.gov.ua search URL to the corresponding API URL.
    
    Args:
        booking_url (str): Input URL, e.g., 
            'https://booking.uz.gov.ua/search-trips/2200001/2210700/list?startDate=2025-05-16'
    
    Returns:
        str: API URL, e.g., 
            'https://app.uz.gov.ua/api/v3/trips?station_from_id=2200001&station_to_id=2210700&with_transfers=0&date=2025-05-16'
    """
    # Split the URL into parts
    parts = booking_url.split('/')
    
    # Extract station IDs
    station_from_id = parts[-3]
    station_to_id = parts[-2]
    
    # Extract date from query parameters
    query_params = parts[-1].split('?')[-1]
    params = dict(param.split('=') for param in query_params.split('&'))
    date = params.get('startDate', '')
    
    # Construct API URL
    api_url = (f"https://app.uz.gov.ua/api/v3/trips?"
               f"station_from_id={station_from_id}&"
               f"station_to_id={station_to_id}&"
               f"with_transfers=0&"
               f"date={date}")
    
    return api_url