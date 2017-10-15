import requests
import json

def get_nearest_city(location):
    limit = 10
    radius = 10000
    latitude = location[0]
    longitude = location[1]

    cities = requests.get('http://getnearbycities.geobytes.com/GetNearbyCities?callback=?&latitude={}&longitude={}&radius={}&limit={}'.format(latitude, longitude, radius, limit))
    text = cities.text[2:-2]
    list = eval(text)
    print(list[4])
    #return cities[0][1]
    # if is_valid_city(city):
    #     return city

def is_valid_city(city):
    return True

def main():
    print(get_nearest_city([50,0]))

if __name__ == "__main__":
    main()