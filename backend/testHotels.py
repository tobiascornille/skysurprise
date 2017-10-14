import requests
import json


def main():
    link = "https://gateway.skyscanner.net/hotels/v1/prices/search/entity/27548283?market=UK&locale=en-GB" \
           "&checkin_date=2018-01-01&checkout_date=2018-01-02&currency=GBP&adults=2&rooms=1&images=3&image_resolution=high" \
           "&boost_official_partners=1&sort=-relevance&limit=30&offset=0&partners_per_hotel=3" \
           "&enhanced=filters,partners,images,location,amenities,extras,query_location&apikey=7772cbd8f1a640ffa9536d96d4c3c48e"

    hotels = requests.get(link, headers={"x-user-agent": "D;B2B"})
    print(hotels.json()["meta"]["status"])
    print('here')
    while hotels.json()["meta"]["status"] != 'COMPLETED':
        requests.get(link)
        print(hotels.json()["meta"]["status"])

if __name__ == "__main__":
    main()