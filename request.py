import json
from darksky.forecast import Forecast
import geopy.geocoders
import requests
from geopy.geocoders import Nominatim

# global vars
authUrl = "auth url"
authInf = {"email": "email", "password": "password"}
geopy.geocoders.options.default_user_agent = 'my_app/1'
geolocator = Nominatim(timeout=60)
dark_key = "dark sky code"  # you get code from loging to darksky

# get access token to access api
r = json.loads(requests.post(authUrl, data=authInf).text)
token = [r[x] for x in r]
for nekaj, drugo in token[0].items():
    token = drugo


# get last_id from /items/weather to use in delete requests
data = json.loads(requests.get("item url ?access_token=" + token).text)
last_id = data["data"][-1]["id"]
last_id_deletion = data["data"][-1]["id"]
first_id = data["data"][0]["id"]


# convert wind_bearing to wind direction
def deg_to(num):
    degrees = (num/22.50) + 0.5
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    return directions[int((degrees % 16))]


# loads cities from /items/cities in an array
def get_cities():
    str_cities = []
    for x in range(1, 11):
        str_x = str(x)
        cities = json.loads(requests.get("item url" + str_x + "?access_token=" + token).text)
        for key, value in cities.items():
            for sub_key, sub_value in value.items():
                if sub_key == "name":
                    str_cities.append(sub_value)
    return str_cities


# get last_id from /items/weather to use in post requests
data = json.loads(requests.get("item url?access_token=" + token).text)

city_no = 1
for city in get_cities():
    lat_long = geolocator.geocode(city)[1]  # get coordinates from city
    napoved = Forecast(float(dark_key), lat_long[0], lat_long[1])  # get weather data for city
    for day in napoved.daily:
        r = requests.post(url="item url" + "?access_token=" + token, json={
            "id": last_id + 1,
            "city": city_no,
            "date": day.time.strftime("%Y-%m-%d"),
            "status": "published",
            "temperature": int(int(day.temperature_max + day.temperature_min)/2),
            "minimum_temperature": int(day.temperature_min),
            "maximum_temperature": int(day.temperature_max),
            "humidity": day.humidity * 100,
            "pressure": int(day.pressure),
            "description": day.summary,
            "wind_direction": str(day.wind_bearing) + " " + deg_to(day.wind_bearing),
            "wind_speed": day.wind_speed,
            "icon": day.icon
        })
        last_id += 1
    city_no += 1


# delete all previously listed cities
for weather_id in range(first_id, last_id_deletion + 1):
    r = requests.delete("item url" + str(weather_id) + "?access_token=" + token)
