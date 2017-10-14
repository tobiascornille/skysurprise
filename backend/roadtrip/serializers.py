from rest_framework import serializers
from backend.roadtrip.models import Roadtrip


class RoadtripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roadtrip
        fields = ('country', 'currency', 'locale', 'originplace',
                    'longitude', 'latitude', 'outbounddate', 'inbounddate',
                    'adults', 'budget', 'rooms')
