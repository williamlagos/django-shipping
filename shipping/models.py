#!/usr/bin/python
#
# This file is part of django-ship project.
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

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now


class DeliverableProperty(models.Model):
    class Meta:
        verbose_name_plural = "Deliverable Properties"

    sku = models.CharField(default="", max_length=20)
    height = models.IntegerField(default=16)
    length = models.IntegerField(default=16)
    width = models.IntegerField(default=16)
    weight = models.FloatField(default=0.1)


class Deliverable(models.Model):
    name = models.CharField(default="((", max_length=50)
    user = models.ForeignKey(User, related_name="+", on_delete=models.CASCADE)
    product = models.IntegerField(default=1)
    mail_code = models.CharField(default="", max_length=100)
    height = models.IntegerField(default=1)
    length = models.IntegerField(default=1)
    width = models.IntegerField(default=1)
    weight = models.IntegerField(default=10)
    value = models.FloatField(default=0.0)
    date = models.DateTimeField(default=now)

    def token(self):
        return self.name[:2]

    def name_trimmed(self):
        return self.name.split(";")[0][1:]

    def month(self):
        return self.date.strftime("%b")


class Amount(models.Model):
    coins = models.IntegerField(default=0)
