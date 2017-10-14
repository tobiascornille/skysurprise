# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from backend.roadtrip.models import Roadtrip
from backend.roadtrip.serializers import RoadtripSerializer
import requests


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
        self.apikey = 'prtl6749387986743898559646983194'


    def plan_trip():
        # find nearest city
        add_nearest_city(self.originplace)
        lastLocation = self.cities[-1]

        # substract the cost to go to this city
        #   is already done in the previous function

        # add as much extra cities as possible within the flightbudget,
        # keeping in mind that we also have to get home
        while flightbudget - self.get_flightprice(lastLocation, self.originplace, self.inbounddate) > 0:
            add_city()

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
            price = self.get_connection_price(self, self.originplace, city, self.outbounddate)
            if price != -1:
                self.flightbudget -= price
                self.cities.append[city[1]]
                return

    def add_city(self, currentcity, date):
        #TODO
        # !!hoeveel dagen per stad?

    def get_connection_price(self, source, destination, date):
        if destination not in citiesoverview:
            return -1

        price = self.get_flightprice(source, destination, date)
        returnprice = self.get_flightprice(destination, self.originplace, self.inbounddate)

        if price + returnprice < self.budget:
            return price

        return -1

    def get_flightprice(self, source, destination, date):
        link = ("http://partners.api.skyscanner.net/apiservices/browseroutes/v1.0/{}/{}/{}/{}/{}/{}/?apikey={}").format(
                self.country, self.currency, self.locale, source, destination, date, self.apikey
                )
        print(link)
        flights = requests.get(link)
        price = flights.json()['Routes'][0]['Price']
        return price
