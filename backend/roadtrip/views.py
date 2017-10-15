# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from backend.roadtrip.models import Roadtrip
from backend.roadtrip.serializers import RoadtripSerializer
import requests
import pickle
from datetime import datetime, timedelta
import os,sys
import json



@api_view(['POST'])
def roadtrip_list(request, format=None):
    request_body = json.loads(request.body)
    roadtrip = RoadtripData(
        country=request_body["country"],
        currency=request_body["currency"],
        locale=request_body["locale"],
        originplace=request_body["originplace"],
        longitude=float(request_body["longitude"]),
        latitude=float(request_body["latitude"]),
        outbounddate=request_body["outbounddate"],
        inbounddate=request_body["inbounddate"],
        adults=int(request_body["adults"]),
        budget=float(request_body["budget"]),
        rooms=int(request_body["rooms"])
    )
    tracker = roadtrip.plan_trip()
    return Response(tracker.to_json())


class RoadtripData:

    def __init__(self, country, currency, locale, originplace, longitude, latitude, outbounddate, inbounddate, adults, budget, rooms):
        self.country = country
        self.currency = currency
        self.locale = locale
        self.originplace = originplace
        self.longitude = longitude
        self.latitude = latitude
        self.outbounddate = outbounddate
        self.inbounddate = inbounddate
        self.adults = adults
        self.budget = budget*adults
        self.flightbudget = budget / 2
        self.hotelbudget = budget / 2
        self.rooms = rooms
        self.days_per_city = 3
        self.apikey = 'prtl6749387986743898559646983194'
        self.tracker = Tracker()

        with open("backend/city_names.pkl", 'rb') as f:
            self.cities_overview = pickle.load(f)

    def plan_trip(self):
        print("start")
        current_day = self.inbounddate

        obj_inbounddate = date_string_to_object(current_day)

        first_flight = self.get_first_flight()
        print("first flight")
        if(first_flight != None):
            self.tracker.flights.append(first_flight)
        else:
            print("couldn't find a trip for you")
            return

        last_city = self.tracker.get_last_city()

        current_day = calculate_new_date(current_day, self.days_per_city)
        obj_next_day = date_string_to_object(calculate_new_date(current_day, self.days_per_city))

        # add as much extra flights as possible within the flightbudget,
        # keeping in mind that we also have to get home in time
        while self.flightbudget > 300:
            print(self.flightbudget)
            flight = self.get_flight(last_city, current_day)
            if(flight != None):
                self.tracker.flights.append(flight)
                last_city = flight["to_destination"]
                print(flight["to_destination"])

                current_day = calculate_new_date(current_day, self.days_per_city)
                obj_next_day = date_string_to_object(current_day)
            else:
                break

        # return flight
        self.tracker.flights.append(self.get_last_flight(last_city,current_day))

        # add the remaining flight money to the hotel budget
        self.hotelbudget += self.flightbudget
        self.flightbudget = 0

        # after finding all our locations, we'll have to find a place to stay for every city
        for index in range(len(self.tracker.flights) - 2):
            hotel = self.get_hotel(index)
            self.tracker.hotels.append(hotel)

        print(self.tracker)
        return self.tracker

    def get_first_flight(self):
        limit = 100000
        radius = 1000000
        latitude = self.latitude
        longitude = self.longitude

        citiesrequest = requests.get('http://getnearbycities.geobytes.com/GetNearbyCities?callback=?&latitude={}&longitude={}&'
                              'radius={}&limit={}'.format(latitude, longitude, radius, limit))
        citiestext = citiesrequest.text[2:-2]
        citieslist = eval(citiestext)

        for city in citieslist:
            city_name = city[1]
            price, destination = self.get_connection_price(self.originplace, city_name, self.outbounddate)
            if price != -1 and price <= self.flightbudget:
                self.flightbudget -= price
                print("found succesful a starting point")
                return {'from_destination': self.originplace,
                        'to_destination': city_name,
                        'departure_flight': self.outbounddate,
                        'arrival_flight': self.outbounddate,
                        'price_flight': price}

        print("failed to find a first city")


    def get_flight(self, current_city, start_date):
        coordinates_json = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address=current_city&key=AIzaSyDSKdFZz_MKA9lwh8kNvDPk9qLz0ocIkQ0')
        latitude = coordinates_json.json()['results'][0]['geometry']['location']['lat']
        longitude = coordinates_json.json()['results'][0]['geometry']['location']['lng']


        limit = 1000
        radius = 10000
        latitude = self.latitude
        longitude = self.longitude
        citiesrequest = requests.get(
            'http://getnearbycities.geobytes.com/GetNearbyCities?callback=?&latitude={}&longitude={}&'
            'radius={}&limit={}'.format(latitude, longitude, radius, limit))
        citiestext = citiesrequest.text[2:-2]
        citieslist = eval(citiestext)

        for city in citieslist:
            city_name = city[1]
            price, destination = self.get_connection_price(current_city, city_name, start_date)
            if price != -1 and price <= 1/2 * self.flightbudget:
                self.flightbudget -= price
                print("found another succesful point")
                return {'from_destination': current_city,
                        'to_destination': city_name,
                        'departure_flight': start_date,
                        'arrival_flight': start_date,
                        'price_flight': price}
        return None


    def get_last_flight(self, current_city, start_date):
        price, destination = self.get_connection_price(current_city, self.originplace, start_date)

        if price > self.flightbudget:
            print("How did we let this happen? :(")
            return None
        else:
            self.flightbudget -= price
            return {'from_destination': current_city,
                    'to_destination': self.originplace,
                    'departure_flight': start_date,
                    'arrival_flight': start_date,
                    'price_flight': price}

    def get_connection_price(self, source, destination, start_date):
        if destination + '\r' not in self.cities_overview:
            return -1, ""
        price, destination = self.get_flight_price(source, destination, start_date)
        return price, destination

    def get_flight_price(self, source, destination, date):
        if (destination != "everywhere"):
            destination = get_autosuggest_id(destination)

        link = ("http://partners.api.skyscanner.net/apiservices/browsequotes/v1.0/{}/{}/{}/{}/{}/{}/?apikey={}").format(
                self.country, self.currency, self.locale, get_autosuggest_id(source), destination, date, self.apikey)
        print(link)
        flights = requests.get(link)
        price = -1
        max_iterations = 1000
        iteration = 0
        final_destination = ""
        while (price == -1 and iteration < max_iterations):
            try:
                price = flights.json()['Quotes'][iteration]['MinPrice']
                final_destination = flights.json()['Places'][iteration]['Name']
            except:
                price = -1
            iteration += 1
        return price, final_destination

    def get_hotel(self, index):
        arriving_flight = self.tracker.flights[index]
        arrival_date = arriving_flight["arrival_flight"]

        departing_flight = self.tracker.flights[index + 1]
        if departing_flight != None:
            departure_date = departing_flight["departure_flight"]

            city_id = get_id(arriving_flight["to_destination"])
            current_hotelbudget = self.hotelbudget / ((len(self.tracker.flights) - 1) - len(self.tracker.hotels))

            link = "https://gateway.skyscanner.net/hotels/v1/prices/search/entity/{}?market={}&locale={}" \
                "&checkin_date={}&checkout_date={}&currency={}&adults={}&rooms={}&price_max={}&sort={}&apikey={}".format(
                    city_id, self.country, self.locale, arrival_date, departure_date, self.currency, self.rooms, self.adults,
                    int(current_hotelbudget), "rating", "7772cbd8f1a640ffa9536d96d4c3c48e")

            print(link)

            hotels = requests.get(link, headers={"x-user-agent": "D;B2B"})

            while hotels.json()["meta"]["status"] != 'COMPLETED':
                hotels = requests.get(link, headers={"x-user-agent": "D;B2B"})

            if(hotels.json()["results"]["hotels"] != None):
                self.hotelbudget -= hotels.json()["results"]["hotels"][0]["offers"][0]["price"]

                return {'hotel_link': hotels.json()["results"]["hotels"][0]["offers"][0]["deeplink"],
                        'hotel_name': hotels.json()["results"]["hotels"][0]["name"],
                        'price_hotel': hotels.json()["results"]["hotels"][0]["offers"][0]["price"]}

        return {'hotel_link': '','hotel_name': '','price_hotel': ''}


class Tracker:

    def __init__(self):
        self.hotels = []
        self.flights = []

    def get_hotels_cost(self):
        sum = 0
        for hotel in self.hotels:
            sum += hotel["price_hotel"]
        return sum

    def get_flights_cost(self):
        sum = 0
        for flight in self.flights:
            sum += flight["price_flight"]
        return sum

    def get_last_city(self):
        try:
            return self.flights[-1]["to_destination"]
        except:
            return None

    def to_json(self):
        output = []
        for idx in range(len(self.flights) - 1):
            current = {}
            current['from_destination_lat'], current['from_destination_long'] = get_location(self.flights[idx]['from_destination'])
            current['from_destination'] = self.flights[idx]['from_destination']
            current['to_destination_lat'], current['to_destination_long'] =  get_location(self.flights[idx]['to_destination'])
            current['to_destination'] = self.flights[idx]['to_destination']
            current['departure_flight'] = self.flights[idx]['departure_flight']
            current['arrival_flight'] = self.flights[idx]['arrival_flight']
            current['price_flight'] = self.flights[idx]['price_flight']
            if idx == len(self.flights)-2:
                current['price_hotel'] = ''
            else:
                print(self.hotels)
                print(idx)
                current['hotel_link'] = self.hotels[idx]['hotel_link']
                current['hotel_name'] = self.hotels[idx]['hotel_name']
                current['price_hotel'] = self.hotels[idx]['price_hotel']
            output.append(current)
        return output





# helper functions
def calculate_new_date(start_date, nb_days):
    delta_days = timedelta(days=nb_days)
    end_date = date_string_to_object(start_date)
    end_date += delta_days
    str_end_date = str(end_date.year) + '-' + str(end_date.month) + '-' + str(end_date.day)
    return str_end_date

def date_string_to_object(str_date):
    str_date = str_date.split('-')
    date = datetime(year=int(str_date[0]), month=int(str_date[1]), day=int(str_date[2]))
    return date

def get_location(city_name):
    api_url = 'http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=true'
    resp = requests.get(api_url%city_name).json()
    lat = resp['results'][0]['geometry']['location']['lat']
    lon = resp['results'][0]['geometry']['location']['lng']
    return (lat, lon)

def get_id(city_name):
    resp = requests.get(
        'http://gateway.skyscanner.net/autosuggest/v3/hotels?q=%s&market=US&locale=en-US&apikey=7772cbd8f1a640ffa9536d96d4c3c48e' % city_name)
    return resp.json()['results'][0]['id']

def get_autosuggest_id(city_name):
    api_url = 'http://partners.api.skyscanner.net/apiservices/autosuggest/v1.0/BE/EUR/nl-NL?query=%s&apiKey=7772cbd8f1a640ffa9536d96d4c3c48e'
    resp = requests.get(api_url%city_name).json()
    return resp['Places'][0]['CityId']

def get_country_id(city_name):
    api_url = 'http://partners.api.skyscanner.net/apiservices/autosuggest/v1.0/BE/EUR/nl-NL?query=%s&apiKey=7772cbd8f1a640ffa9536d96d4c3c48e'
    resp = requests.get(api_url%city_name).json()
    return resp['Places'][0]['CountryId']
