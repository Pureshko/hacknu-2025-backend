import requests
import json
from urllib.parse import urlencode

API_KEY = "401b0774-dbe8-4f70-91c9-697adac3e650"
BASE_URL = "https://catalog.api.2gis.com/2.0/region/search"

def search_region(query: str):
    params = {
        "q": query,
        "key": API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    return data

