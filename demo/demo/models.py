#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of Efforia Open Source Initiative.
#
# Copyright (C) 2011-2016 William Oliveira de Lagos <william@efforia.com.br>
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

from django.db.models import ForeignKey,TextField,CharField,IntegerField,DateTimeField,BooleanField,Model,FloatField
from django.contrib.auth.models import User
from django.utils.timezone import now
import sys,os,json

locale = ('Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez')

class Spreaded(Model):
    name = CharField(default='!!',max_length=10)
    user = ForeignKey(User,related_name='+')
    spread = IntegerField(default=1)
    spreaded = IntegerField(default=2)
    date = DateTimeField(default=now)
    def token(self): return self.name[:2]
    def stoken(self): return self.name[:1]
    def month(self): return locale[self.date.month-1]

class Spreadable(Model):
    name = CharField(default='',max_length=50)
    user = ForeignKey(User,related_name='+')
    content = TextField()
    spreaded = CharField(default='efforia',max_length=15)
    date = DateTimeField(default=now)
    def token(self): return self.name[:1]
    def name_trimmed(self): return self.name[1:]
    def month(self): return locale[self.date.month-1]

class Playable(Model):
    name = CharField(default='',max_length=150)
    user = ForeignKey(User,related_name='+')
    category = IntegerField(default=1)
    description = TextField()
    token = CharField(max_length=20)
    credit = IntegerField(default=0)
    visual = CharField(default='',max_length=40)
    date = DateTimeField(default=now)
    def etoken(self): return self.name[:1]
    def name_trimmed(self): return self.name[1:]
    def month(self): return locale[self.date.month-1]
    def date_formatted(self): return self.date.strftime('%Y-%m-%d %H:%M:%S.%f')

class Image(Model):
    name = CharField(default='!%',max_length=10)
    description = CharField(default='',max_length=140)
    link = CharField(default='',max_length=100)
    user = ForeignKey(User,related_name='+')
    date = DateTimeField(default=now)
    def token(self): return self.name[:2]
    def name_trimmed(self): return self.name[2:]
    def month(self): return locale[self.date.month-1]
    def visual(self):
        client = httpclient.HTTPClient()
        response = client.fetch(self.visual)
        url = '%s?dl=1' % response.effective_url
        return url
