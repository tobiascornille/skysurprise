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
        self.flightbudget = budget / ..
        self.rooms = rooms
        self.cities = []

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
                self.budget -= price
                self.cities.append[city[1]]
                return

    def add_city(self, currentcity, date):
        #TODO

    def get_connection_price(self, source, destination, date):
        if destination not in citiesoverview:
            return -1

        price = self.get_flightprice(source, destination, date)
        returnprice = self.get_flightprice(destination, self.originplace, self.inbounddate)

        if price + returnprice < self.budget:
            return price

        return -1


# helper function
def get_flights(roadtripData):
    country = roadtripData['country']
    currency = roadtripData['currency']
    locale = roadtripData['locale']
    originplace = roadtripData['originplace']
    # ....






def main():
    print(get_nearest_city([41,2]))

if __name__ == "__main__":
    main()
