#!/usr/bin/python
#
# This file is part of django-shipping project.
#
# Copyright (C) 2011-2020 William Oliveira de Lagos <william.lagos@icloud.com>
#
# Shipping is free software: you can redistribute it and/or modify
# it under the terms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Shipping is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Shipping. If not, see <http://www.gnu.org/licenses/>.
#

from django.test import TestCase

from shipping.providers.correios import CorreiosShippingService
from shipping.providers.fretefacil import FreteFacilShippingService


class FreteFacilShippingServiceTest(TestCase):
    def setUp(self):
        self.service = FreteFacilShippingService()

    def test_create_deliverable_valid(self):
        result = self.service.create_deliverable(
            "91350-180", "01310-100", "20", "5", "20", "1.0"
        )
        self.assertIsInstance(result, dict)
        self.assertEqual(result["sender"], "91350-180")
        self.assertEqual(result["receiver"], "01310-100")

    def test_create_deliverable_height_too_small(self):
        result = self.service.create_deliverable(
            "91350-180", "01310-100", "20", "1", "20", "1.0"
        )
        self.assertIsInstance(result, str)
        self.assertIn("mínimo", result)

    def test_create_deliverable_width_too_small(self):
        result = self.service.create_deliverable(
            "91350-180", "01310-100", "5", "5", "20", "1.0"
        )
        self.assertIsInstance(result, str)
        self.assertIn("mínimo", result)

    def test_create_deliverable_length_too_small(self):
        result = self.service.create_deliverable(
            "91350-180", "01310-100", "20", "5", "10", "1.0"
        )
        self.assertIsInstance(result, str)
        self.assertIn("mínimo", result)


class CorreiosShippingServiceTest(TestCase):
    def setUp(self):
        self.service = CorreiosShippingService()

    def test_validate_sets_minimum_height(self):
        self.service.altura = 0
        self.service._validate()
        self.assertGreaterEqual(self.service.altura, 2)

    def test_validate_sets_minimum_comprimento(self):
        self.service.comprimento = 0
        self.service._validate()
        self.assertGreaterEqual(self.service.comprimento, 16)

    def test_validate_sets_minimum_peso(self):
        self.service.peso = 0.0
        self.service._validate()
        self.assertGreaterEqual(self.service.peso, 0.3)

    def test_validate_largura_package_constraint(self):
        self.service.formato = "PACOTE"
        self.service.largura = 5
        self.service.comprimento = 20
        self.service._validate()
        self.assertGreaterEqual(self.service.largura, 11)

    def test_validate_rolo_format(self):
        self.service.formato = "ROLO"
        self.service.diametro = 0
        self.service.comprimento = 0
        self.service._validate()
        self.assertGreaterEqual(self.service.diametro, 5)
        self.assertGreaterEqual(self.service.comprimento, 18)
