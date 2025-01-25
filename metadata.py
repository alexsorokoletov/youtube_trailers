import requests

def get_movie_data(title, year, api_key):
    url = f"http://www.omdbapi.com/?s={title}&y={year}&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to fetch data"}
