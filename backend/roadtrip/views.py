# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from backend.roadtrip.models import Roadtrip
from backend.roadtrip.serializers import RoadtripSerializer
import requests
from datetime import datetime, timedelta


@api_view(['GET', 'POST'])
def roadtrip_list(request, format=None):
    if request.method == 'GET':
        roadtrips = Roadtrip.objects.all()
        lastRoadtrip = RoadtripSerializer(Roadtrip.objects.last(), many=False)
        # serializer = RoadtripSerializer(roadtrips, many=True)
        # print(lastRoadtrip.data['source'])
        return Response(lastRoadtrip.data)

    elif request.method == 'POST':
        serializer = RoadtripSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoadtripData:

    def __init__(self, country, currency, locale, originplace, destinationplace, outbounddate, inbounddate, adults, budget, rooms, randomlocation):
        self.country = country
        self.currency = currency
        self.locale = locale
        self.originplace = originplace
        self.destinationplace = destinationplace
        self.outbounddate = outbounddate
        self.inbounddate = inbounddate
        self.adults = adults
        self.budget = budget
        self.flightbudget = budget / 2
        self.rooms = rooms
        self.cities = []
        self.days_per_city = 3
        self.apikey = 'prtl6749387986743898559646983194'


    def plan_trip():
        day_in_planning = self.inbounddate
        # find nearest city
        add_nearest_city(self.originplace)
        last_city = self.cities[-1]
        if last_city == None:
            print("couldn't find a trip for you")
            return

        # substract the cost to go to this city
        #   is already done in the previous function

        # update day_in_planning
        day_in_planning = calculate_new_date(day_in_planning, days_per_city)

        # add as much extra cities as possible within the flightbudget,
        # keeping in mind that we also have to get home
        while flightbudget - self.get_flightprice(lastLocation, self.originplace, self.inbounddate) > 0:
            add_city(last_city, day_in_planning, days_per_city)
            last_city = self.cities[-1]

        # terugvlucht moeten aftrekken

        # after finding all our locations, we'll have to find a place to stay for the night


    def add_nearest_city(self, location):
        limit = 100
        radius = 10000
        latitude = location[0]
        longitude = location[1]

        cities = requests.get(
            'http://getnearbycities.geobytes.com/GetNearbyCities?callback=?&latitude=%s&longitude=%s&radius=%i&limit=%i' % (
            latitude, longitude, radius, limit))
        citiestext = cities.text[2:-2]
        citieslist = eval(citiestext)

        for city in citieslist:
            price = self.get_connection_price(self, location, city, self.outbounddate, self.inbounddate)
            if price != -1:
                self.flightbudget -= price
                self.cities.append[city[1]]
                return

    def add_city(self, current_city, start_date, nb_days):
        end_date = calculate_new_date(start_date, nb_days)
        price = get_connection_price(current_city, "everywhere", start_date, end_date)
        if price == -1:
            print("failed to find a new city. Abort mission")
            return
        else:
            self.flightbudget -= price
            self.cities.append[city[1]]

    def get_connection_price(self, source, destination, start_date, end_date):
        if destination not in citiesoverview:
            return -1

        price = self.get_flightprice(source, destination, start_date)
        returnprice = self.get_flightprice(destination, self.originplace, end_date)

        if price + returnprice < self.budget:
            return price

        return -1

    def get_flightprice(self, source, destination, date):
        link = ("http://partners.api.skyscanner.net/apiservices/browseroutes/v1.0/{}/{}/{}/{}/{}/{}/?apikey={}").format(
                self.country, self.currency, self.locale, source, destination, date, self.apikey
                )
        print(link)
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

    # helper
    def calculate_new_date(start_date, nb_days):
        start_date = start_date.split('-')
        delta_days = timedelta(days=nb_days)
        end_date = datetime.datetime(year=int(start_date[0], month=int(start_date[1]), day=int(start_date[2])))
        end_date += delta_days
        str_end_date = str(end_date.year) + '-' + str(end_date.month) + '-' + str(end_date.day)
        return str_end_date
