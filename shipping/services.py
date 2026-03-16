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

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render

from .models import Deliverable


def user(name):
    return User.objects.filter(username=name)[0]


def superuser():
    return User.objects.filter(is_superuser=True)[0]


def send_invoice(request):
    send_mail(
        "Subject here",
        "Here is the message.",
        "contato@efforia.com.br",
        ["william.lagos1@gmail.com"],
        fail_silently=False,
    )
    return HttpResponse("E-mail sended.")


class ShippingService:
    model = Deliverable

    def __init__(self):
        pass

    def verify_permissions(self, request):
        perm = "super"
        if "permissions" in request.COOKIES:
            perm = request.COOKIES["permissions"]
        permissions = "super" in perm
        return permissions

    def start(self, request):
        u = user("efforia")
        permissions = self.verify_permissions(request)
        actions = settings.EFFORIA_ACTIONS
        apps = []
        for a in settings.EFFORIA_APPS:
            apps.append(actions[a])
        return render(
            request,
            "interface.html",
            {
                "static_url": settings.STATIC_URL,
                "user": user("efforia"),
                "perm": permissions,
                "name": f"{u.first_name} {u.last_name}",
                "apps": apps,
            },
            content_type="text/html",
        )

    def postal_code(self, request):
        from .providers.correios import CorreiosCode
        from .providers.fretefacil import FreteFacilShippingService

        u = self.current_user(request)
        s = ""
        mail_code = request.GET["address"]
        code = CorreiosCode()
        q = code.consulta(mail_code)
        fretefacil = FreteFacilShippingService()
        d = fretefacil.create_deliverable(
            "91350-180", mail_code, "30", "30", "30", "0.5"
        )
        value = fretefacil.delivery_value(d)
        formatted = f'<div>Valor do frete: R$ <div style="display:inline;" class="delivery">{value}</div></div>'
        for i in q.values():
            s += f"<div>{i}\n</div>"
        s += formatted
        deliverable = Deliverable(
            buyer=u,
            mail_code=mail_code,
            code=d["sender"],
            receiver=d["receiver"],
            height=int(d["height"]),
            length=int(d["length"]),
            width=int(d["width"]),
            weight=int(float(d["weight"][0]) * 1000.0),
            value=value,
        )
        deliverable.save()
        return HttpResponse(s)

    def view_package(self, request):
        form_data = {}
        if "quantity" in request.GET:
            quantity = request.GET["quantity"]
            credit = int(request.GET["credit"])
        else:
            quantity = 1
            credit = 1
        paypal_dict = {
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "amount": "1.00",
            "item_name": "Produto do Plethora",
            "invoice": "unique-invoice-id",
            "notify_url": "http://www.efforia.com.br/paypal",
            "return_url": "http://www.efforia.com.br/delivery",
            "cancel_return": "http://www.efforia.com.br/cancel",
            "currency_code": "BRL",
            "quantity": quantity,
        }
        return render(
            request,
            "delivery.html",
            {
                "paypal": paypal_dict,
                "credit": credit,
                "form": form_data,
            },
            content_type="text/html",
        )

    def create_package(self, request):
        return HttpResponse("OK")


class AmountService:
    def discharge(self, request):
        import json

        userid = request.POST["userid"]
        values = request.POST["value"]
        from django.contrib.auth.models import User

        u = User.objects.filter(pk=int(userid))[0]
        profile = getattr(u, "profile", None)
        if profile:
            profile.credit -= int(values)
            profile.save()
        return HttpResponse(
            json.dumps(
                {"objects": {"userid": userid, "value": getattr(profile, "credit", 0)}}
            ),
            content_type="application/json",
        )

    def recharge(self, request):
        import json

        userid = request.POST["userid"]
        values = request.POST["value"]
        from django.contrib.auth.models import User

        u = User.objects.filter(pk=int(userid))[0]
        profile = getattr(u, "profile", None)
        if profile:
            profile.credit += int(values)
            profile.save()
        return HttpResponse(
            json.dumps(
                {"objects": {"userid": userid, "value": getattr(profile, "credit", 0)}}
            ),
            content_type="application/json",
        )

    def balance(self, request):
        import json

        userid = request.GET["userid"]
        from django.contrib.auth.models import User

        u = User.objects.filter(pk=int(userid))[0]
        profile = getattr(u, "profile", None)
        return HttpResponse(
            json.dumps(
                {"objects": {"userid": userid, "value": getattr(profile, "credit", 0)}}
            ),
            content_type="application/json",
        )


class RateService:
    def calculate(self, data):
        # TODO: Rebuild calculate logic
        return {"success": "calculated"}
