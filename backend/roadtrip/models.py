# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.
class Roadtrip(models.Model):
    country = models.CharField(max_length=50, default="BE")
    currency = models.CharField(max_length=10, default="EUR")
    locale = models.CharField(max_length=50, default="nl-NL")
    originplace = models.CharField(max_length=50, default="BE")
    longitude = models.FloatField(default=4.7005176)
    latitude = models.FloatField(default=50.8798438)
    outbounddate = models.DateField(default="2017-11-11")
    inbounddate = models.DateField(default="2017-11-23")
    adults = models.PositiveIntegerField(1, default=2)
    budget = models.FloatField(1)
    rooms = models.PositiveIntegerField(1, default=1)
