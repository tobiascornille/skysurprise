# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.
class Roadtrip(models.Model):
    country = models.CharField(max_length=50, default="BE")
    currency = models.CharField(max_length=10, default="EUR")
    locale = models.CharField(max_length=50, default="nl-NL")
    originplace = models.CharField(max_length=50, default="BE")
    destinationplace = models.CharField(max_length=50, default="GB")
    outbounddate = models.DateField(auto_now_add=True)
    inbounddate = models.DateField(auto_now_add=True)
    adults = models.PositiveIntegerField(1)
    budget = models.FloatField(500.0)
    rooms = models.PositiveIntegerField(1)
