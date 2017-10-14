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



@api_view(['GET', 'POST'])
def roadtrip_list(request, format=None):
    if request.method == 'GET':
        roadtrips = Roadtrip.objects.all()
        lastRoadtrip = RoadtripSerializer(Roadtrip.objects.last(), many=False)

        # Initialize roadtrip data
        roadtrip_data = RoadtripData(
            country=lastRoadtrip.data['country'],
            currency=lastRoadtrip.data['currency'],
            locale=lastRoadtrip.data['locale'],
            originplace=lastRoadtrip.data['originplace'],
            destinationplace=lastRoadtrip.data['destinationplace'],
            outbounddate=lastRoadtrip.data['outbounddate'],
            inbounddate=lastRoadtrip.data['inbounddate'],
            adults=lastRoadtrip.data['adults'],
            budget=lastRoadtrip.data['budget'],
            rooms=lastRoadtrip.data['rooms'],
            randomlocation='Brussels International'
        )
        roadtrip_data.plan_trip()
        return Response(lastRoadtrip.data)

    elif request.method == 'POST':
        serializer = RoadtripSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        self.budget = budget
        self.flightbudget = budget / 2
        self.hotelbudget = budget / 2
        self.rooms = rooms
        self.cities = []
        self.hotels = []
        self.days_per_city = 3
        self.apikey = 'prtl6749387986743898559646983194'

        with open("backend\city_names.pkl", 'rb') as f:
            self.cities_overview = pickle.load(f)


    def plan_trip(self):
        day_in_planning = self.inbounddate
        obj_inbounddate = date_string_to_object(self.inbounddate)

        # find nearest city from given (random) location
        self.add_starting_city()
        if len(self.cities) == 0:
            print("couldn't find a trip for you")
            return

        last_city = self.cities[-1]
        # substract the cost to go to this city
        #   is already done in the previous function

        # update day_in_planning
        day_in_planning = calculate_new_date(day_in_planning, self.days_per_city)

        obj_next_day_in_planning = date_string_to_object(calculate_new_date(day_in_planning, self.days_per_city))

        # add as much extra cities as possible within the flightbudget,
        # keeping in mind that we also have to get home in time
        while (self.flightbudget - self.get_flightprice(last_city, self.originplace, self.inbounddate)) > 0 and obj_next_day_in_planning <= obj_inbounddate:
            self.add_city(last_city, day_in_planning, self.days_per_city)
            last_city = self.cities[-1]

            day_in_planning = calculate_new_date(day_in_planning, self.days_per_city)
            obj_next_day_in_planning = date_string_to_object(day_in_planning)

        # terugvlucht moeten aftrekken
        
        # after finding all our locations, we'll have to find a place to stay for the night

    def get_id(self, city_name):
        resp = requests.get(
            'http://gateway.skyscanner.net/autosuggest/v3/hotels?q=%s&market=US&locale=en-US&apikey=7772cbd8f1a640ffa9536d96d4c3c48e' % city_name)
        return resp.json()['results'][0]['id']


    def add_hotel(self, city, checkindate, checkoutdate, currenthotelnumber):
        cityid = self.get_id(city)
        thishotelbudget = self.hotelbudget / (len(self.cities) - currenthotelnumber)

        link = "https://gateway.skyscanner.net/hotels/v1/prices/search/entity/{}?market={}&locale={}" \
               "&checkin_date={}&checkout_date={}&currency={}&adults={}&rooms={}&price_max={}&sort={}?apikey={}".format(
                cityid, self.country, self.locale, checkindate, checkoutdate, self.currency, self.rooms, self.adults,
                thishotelbudget, "rating", "7772cbd8f1a640ffa9536d96d4c3c48e")

        hotels = requests.get(link, headers={"x-user-agent": "D;B2B"})

        while hotels.json()["meta"]["status"] != 'COMPLETED':
            hotels = requests.get(link)

        self.hotelbudget -= hotels["offers"][0]
        self.hotels.append(hotels["results"][0])


    def add_starting_city(self):
        limit = 100
        radius = 10000
        latitude = self.latitude
        longitude = self.longitude
        citiesreq = requests.get('http://getnearbycities.geobytes.com/GetNearbyCities?callback=?&latitude={}&longitude={}&'
                              'radius={}&limit={}'.format(latitude, longitude, radius, limit))
        citiestext = citiesreq.text[2:-2]
        citieslist = eval(citiestext)

        end_date = calculate_new_date(self.outbounddate, self.days_per_city)

        for city in citieslist:
            price = self.get_connection_price(self.originplace, city, self.outbounddate, end_date)
            if price != -1:
                self.flightbudget -= price
                self.cities.append(city)
                return

        print("failed to find a new city. Abort mission")


    def add_city(self, current_city, start_date, nb_days):
        end_date = calculate_new_date(start_date, nb_days)
        price = self.get_connection_price(current_city, "everywhere", start_date, end_date)
        if price == -1:
            print("failed to find a new city. Abort mission")
            return
        else:
            self.flightbudget -= price
            self.cities.append(current_city)

    def get_connection_price(self, source, destination, start_date, end_date):
        if destination + '\r' not in self.cities_overview:
            return -1

        price = self.get_flightprice(source, destination, start_date)
        returnprice = self.get_flightprice(destination, self.originplace, end_date)

        if price + returnprice < 1/2 * self.flightbudget: # Half so we have enough budget for the rest of the trip
            return price

        return -1

    def get_flightprice(self, source, destination, date):
        link = ("http://partners.api.skyscanner.net/apiservices/browseroutes/v1.0/{}/{}/{}/{}/{}/{}/?apikey={}").format(
                self.country, self.currency, self.locale, source, destination, date, self.apikey
                )
        flights = requests.get(link)

        price = -1
        max_iterations = 1000
        iteration = 0
        while (price == -1 and iteration < max_iterations):
            try:
                price = flights.json()['Routes'][iteration]['Price']
            except:
                price = -1
        return price

# helpers
def calculate_new_date(start_date, nb_days):
    delta_days = timedelta(days=nb_days)
    end_date = date_string_to_object(start_date)
    end_date += delta_days
    str_end_date = str(end_date.year) + '-' + str(end_date.month) + '-' + str(end_date.day)
    return str_end_date

def date_string_to_object(str_date):
    str_date = str_date.split('-')
    date = datetime(year=int(str_date[0]), month=int(str_date[1]), day=int(str_date[2]))

def get_location(city_name):
    api_url = 'http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=true'
    resp = requests.get(api_url%city_name).json()
    lat = resp['results'][0]['geometry']['location']['lat']
    lon = resp['results'][0]['geometry']['location']['lng']
    return (lat, lon)
