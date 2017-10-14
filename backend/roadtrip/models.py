# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.
class Roadtrip(models.Model):
    # startDate = models.DateField(auto_now_add=True)
    # endDate = models.DateField(auto_now_add=True)
    source = models.CharField(max_length=50)
    count = models.PositiveIntegerField(1)
    budget = models.FloatField(500.0)
    rooms = models.PositiveIntegerField(1)
