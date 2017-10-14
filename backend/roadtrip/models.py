# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Roadtrip(models.model):
    # departureRangeStart = models.DateField(auto_now_add=True)
    # departureRangeStop = models.DateField(auto_now_add=True)
    # arrivalRangeStart = models.DateField(auto_now_add=True)
    # arrivalRangeStop = models.DateField(auto_now_add=True)
    source = models.CharField()
    count = models.PositiveIntegerField(1)
    budget = models.FloatField(500.0)
    rooms = models.PositiveIntegerField(1)