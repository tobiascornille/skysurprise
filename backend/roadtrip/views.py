# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from backend.roadtrip.models import Roadtrip
from backend.roadtrip.serializers import RoadtripSerializer


@api_view(['GET', 'POST'])
def roadtrip_list(request, format=None):
    if request.method == 'GET':
        roadtrips = Roadtrip.objects.all()
        serializer = RoadtripSerializer(roadtrips, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = RoadtripSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
