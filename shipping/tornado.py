#!/usr/bin/python
# -*- coding: utf-8 -*-

from tornado.httpclient import HTTPClient as Client
from tornado.httpclient import HTTPRequest as Request

def request(url,headers,xml):
	request = Request(url,headers=headers,body=xml,method='POST')
        client = Client()
        response = client.fetch(request)
	return response.body
