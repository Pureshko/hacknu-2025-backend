import requests
import json
from config import API_KEY, DEFAULT_REGION_ID

BASE_URL = "https://catalog.api.2gis.com/3.0/items"

def get_rubric_id(rubric_id, region_id):
    params = {"rubric_id": rubric_id, "region_id": region_id, "key": API_KEY}
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return data

if __name__ == '__main__':
    print(get_rubric_id(547, DEFAULT_REGION_ID))

