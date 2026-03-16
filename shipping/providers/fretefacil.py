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

from urllib.request import Request, urlopen
from xml.dom import minidom as dom

from shipping.strings import (
    FRETEFACIL_CANNOT_CALCULATE,
    FRETEFACIL_HEIGHT_TOO_SMALL,
    FRETEFACIL_LENGTH_TOO_SMALL,
    FRETEFACIL_WIDTH_TOO_SMALL,
)


class FreteFacilShippingService:
    def create_deliverable(self, sender, receiver, width, height, length, weight):
        if int(height) < 2:
            return str(FRETEFACIL_HEIGHT_TOO_SMALL)
        if int(width) < 11:
            return str(FRETEFACIL_WIDTH_TOO_SMALL)
        if int(length) < 16:
            return str(FRETEFACIL_LENGTH_TOO_SMALL)
        deliverable = {
            "sender": sender,
            "receiver": receiver,
            "width": str(width),
            "height": str(height),
            "length": str(length),
            "weight": str(weight),
        }
        return deliverable

    def build_request(self, d):
        url = "https://ff.paypal-brasil.com.br/FretesPayPalWS/WSFretesPayPal"
        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SoapAction": f"{url}/getPreco",
        }
        xml = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:shipping="https://ff.paypal-brasil.com.br/FretesPayPalWS">
        <soapenv:Header />
          <soapenv:Body>
            <shipping:getPreco>
              <cepOrigem>{}</cepOrigem>
              <cepDestino>{}</cepDestino>
              <largura>{}</largura>
              <altura>{}</altura>
              <profundidade>{}</profundidade>
              <peso>{}</peso>
            </shipping:getPreco>
          </soapenv:Body>
        </soapenv:Envelope>""".format(
            d["sender"],
            d["receiver"],
            d["width"],
            d["height"],
            d["length"],
            d["weight"],
        )
        return url, headers, xml

    def delivery_value(self, deliverable):
        url, headers, xml = self.build_request(deliverable)
        req = Request(url, xml.encode("utf-8"), headers)
        value = urlopen(req).read()
        val = (
            dom.parseString(value)
            .getElementsByTagName("return")[0]
            .childNodes[0]
            .wholeText
        )
        if "-2.0" in val:
            return str(FRETEFACIL_CANNOT_CALCULATE)
        else:
            return f"{float(val):.2f}"
