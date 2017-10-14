from django.contrib.auth.models import User, Group
from rest_framework import serializers
from roadtrip.models import Roadtrip


class RoadtripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roadtrip
        fields = ('source', 'count', 'budget', 'rooms')