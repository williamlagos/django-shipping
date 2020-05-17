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

from django.utils.translation import ugettext as _

try:
    from mezzanine.conf import settings
    from cartridge.shop.utils import set_shipping
    from cartridge.shop.models import Cart
    from cartridge.shop.forms import OrderForm
except ImportError as e:
    pass

from shipping.codes import CorreiosCode
from shipping.fretefacil import FreteFacilShippingService
from shipping.correios import CorreiosShippingService
from shipping.models import DeliverableProperty

def fretefacil_shipping_handler(request, form, order=None):
    if request.session.get("free_shipping"): return
    settings.use_editable()
    if form is not None: user_postcode = form.cleaned_data['shipping_detail_postcode']
    else: user_postcode = settings.STORE_POSTCODE 
    user_postcode = form.cleaned_data['shipping_detail_postcode']
    shippingservice = FreteFacilShippingService()
    cart = Cart.objects.from_request(request)
    delivery_value = 0.0
    if cart.has_items():
        for product in cart:
            properties = DeliverableProperty.objects.filter(sku=product.sku)
            if len(properties) > 0:
                props = properties[0]
                deliverable = shippingservice.create_deliverable(settings.STORE_POSTCODE,
                                                                 user_postcode,
                                                                 props.width,
                                                                 props.height,
                                                                 props.length,
                                                                 props.weight)
                delivery_value += float(shippingservice.delivery_value(deliverable))
    set_shipping(request, _("Correios"),delivery_value)

def correios_create_deliverable(obj,service,store_postcode,user_postcode,width,height,length,weight):
    obj.cep_origem = store_postcode
    obj.altura = height
    obj.largura = width
    obj.comprimento = length
    obj.peso = weight
    obj.servico = service
    return {
        'postcode':user_postcode,
        'service':service
    }


def correios_delivery_value(shippingservice,deliverable):
    shippingservice(deliverable['postcode'],deliverable['service'])
    return '.'.join(shippingservice.results[deliverable['service']][1].split(','))

def sedex_shipping_handler(request, form, order=None):
    if request.session.get("free_shipping"): return
    settings.use_editable()
    if form is not None: user_postcode = form.cleaned_data['shipping_detail_postcode']
    else: user_postcode = settings.STORE_POSTCODE
    shippingservice = CorreiosShippingService()
    cart = Cart.objects.from_request(request)
    delivery_value = 0.0
    if cart.has_items():
        for product in cart:
            properties = DeliverableProperty.objects.filter(sku=product.sku)
            if len(properties) > 0:
                props = properties[0]
                deliverable = correios_create_deliverable(shippingservice,
                                                          'SEDEX',
                                                          settings.STORE_POSTCODE,
                                                          user_postcode,
                                                          props.width,
                                                          props.height,
                                                          props.length,
                                                          props.weight)
                delivery_value += float(correios_delivery_value(shippingservice,deliverable))
    set_shipping(request, _("Correios"),delivery_value)

def shipping_payment_handler(request, order_form, order):
    data = order_form.cleaned_data
    shipping = order.shipping_total
    code = CorreiosCode()
    shipping_data = code.consulta(order.billing_detail_postcode)
    order.billing_detail_street  = '%s %s %s' % (shipping_data['tipo_logradouro'],
                                                 shipping_data['logradouro'],
                                                 data['billing_detail_complement'])
    order.billing_detail_city    = shipping_data['cidade']
    order.billing_detail_state   = shipping_data['uf']
    order.billing_detail_country = settings.STORE_COUNTRY
    order.save()
    currency = settings.SHOP_CURRENCY
    cart = Cart.objects.from_request(request)
    cart_items = []
    has_shipping = False
    for item in cart.items.all():
        quantity = len(DeliverableProperty.objects.filter(sku=item.sku))
        if quantity > 0: has_shipping = True
        cart_items.append({
            "name":item.description,
            "sku":item.sku,
            "price":'%.2f' % item.unit_price,
            "currency":currency,
            "quantity":item.quantity
        })
    if has_shipping:
        cart_items.append({
            "name": "Frete via SEDEX",
            "sku":"1",
            "price":'%.2f' % shipping,
            "currency":currency,
            "quantity":1
        })
    return shipping