# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from views import get_nearest_city

# Create your tests here.
get_nearest_city([41,2]);

class CityTestCase(TestCase):
    #def setUp(self):
    def test_get_nearest_city(self):
        self.assertEqual(get_nearest_city([41,2]), 'Vilanova I La Geltru')