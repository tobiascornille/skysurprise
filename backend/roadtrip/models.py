# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.
class Roadtrip(models.Model):
    country = models.CharField(max_length=50, default="BE")
    currency = models.CharField(max_length=10, default="EUR")
    locale = models.CharField(max_length=50, default="nl-NL")
    originplace = models.CharField(max_length=50, default="BE")
    longitude = models.FloatField(default="0.0")
    latitude = models.FloatField(default="0.0")
    outbounddate = models.DateField(default="1900-10-10")
    inbounddate = models.DateField(default="1900-10-10")
    adults = models.PositiveIntegerField(1, default="0")
    budget = models.FloatField(default="0.0")
    rooms = models.PositiveIntegerField(1, default="0")
