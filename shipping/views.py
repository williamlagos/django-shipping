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

import json

from django.http import JsonResponse
from django.views import View

from .models import Cart, CartItem, Order, Product


class DeliveriesView(View):
    def get(self, request):
        return JsonResponse({"deliveries": "success"})


class ProductsView(View):
    def get(self, request):
        products = list(
            Product.objects.filter(available=True).values(
                "id", "name", "slug", "description", "price", "sku"
            )
        )
        return JsonResponse({"products": products})


class CartView(View):
    def get(self, request):
        cart = self._get_cart(request)
        items = [
            {
                "product_id": item.product_id,
                "product_name": item.product.name,
                "quantity": item.quantity,
                "subtotal": str(item.subtotal()),
            }
            for item in cart.items.select_related("product").all()
        ]
        return JsonResponse({"cart_id": cart.pk, "items": items, "total": str(cart.total())})

    def post(self, request):
        try:
            data = json.loads(request.body)
            product_id = data["product_id"]
            quantity = int(data.get("quantity", 1))
        except (KeyError, ValueError, json.JSONDecodeError):
            return JsonResponse({"error": "Invalid request"}, status=400)

        try:
            product = Product.objects.get(pk=product_id, available=True)
        except Product.DoesNotExist:
            return JsonResponse({"error": "Product not found"}, status=404)

        cart = self._get_cart(request)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()
        return JsonResponse({"cart_id": cart.pk, "product_id": product.pk, "quantity": item.quantity})

    def _get_cart(self, request):
        user = request.user if request.user.is_authenticated else None
        if user:
            cart, _ = Cart.objects.get_or_create(
                user=user, defaults={"session_key": request.session.session_key or ""}
            )
        else:
            if not request.session.session_key:
                request.session.create()
            cart, _ = Cart.objects.get_or_create(
                session_key=request.session.session_key, user=None
            )
        return cart


class OrdersView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)
        orders = list(
            Order.objects.filter(user=request.user).values(
                "id", "status", "total", "created"
            )
        )
        return JsonResponse({"orders": orders})

