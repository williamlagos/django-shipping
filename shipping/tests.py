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

import json
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from shipping.models import Cart, CartItem, Category, Order, OrderItem, Product
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


class CategoryModelTest(TestCase):
    def test_str(self):
        category = Category(name="Eletrônicos", slug="eletronicos")
        self.assertEqual(str(category), "Eletrônicos")


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Eletrônicos", slug="eletronicos")
        self.product = Product.objects.create(
            name="Notebook",
            slug="notebook",
            price=Decimal("2999.99"),
            sku="NB-001",
            category=self.category,
        )

    def test_str(self):
        self.assertEqual(str(self.product), "Notebook")

    def test_available_default(self):
        self.assertTrue(self.product.available)

    def test_category_relationship(self):
        self.assertEqual(self.product.category, self.category)
        self.assertIn(self.product, self.category.products.all())


class CartModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass")
        self.product = Product.objects.create(
            name="Mouse",
            slug="mouse",
            price=Decimal("99.90"),
            sku="MS-001",
        )
        self.cart = Cart.objects.create(user=self.user)

    def test_str(self):
        self.assertIn("Cart", str(self.cart))

    def test_empty_total(self):
        self.assertEqual(self.cart.total(), 0)

    def test_total_with_items(self):
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        self.assertEqual(self.cart.total(), Decimal("199.80"))

    def test_cartitem_subtotal(self):
        item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=3)
        self.assertEqual(item.subtotal(), Decimal("299.70"))

    def test_cartitem_str(self):
        item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)
        self.assertIn("Mouse", str(item))


class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="pass")
        self.product = Product.objects.create(
            name="Teclado",
            slug="teclado",
            price=Decimal("199.00"),
            sku="KB-001",
        )
        self.order = Order.objects.create(
            user=self.user,
            total=Decimal("199.00"),
        )

    def test_default_status(self):
        self.assertEqual(self.order.status, Order.STATUS_PENDING)

    def test_str(self):
        self.assertIn("Order", str(self.order))
        self.assertIn("pending", str(self.order))

    def test_status_choices(self):
        statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        self.assertIn(Order.STATUS_PENDING, statuses)
        self.assertIn(Order.STATUS_PAID, statuses)
        self.assertIn(Order.STATUS_SHIPPED, statuses)
        self.assertIn(Order.STATUS_DELIVERED, statuses)
        self.assertIn(Order.STATUS_CANCELLED, statuses)

    def test_orderitem_subtotal(self):
        item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=Decimal("199.00"),
        )
        self.assertEqual(item.subtotal(), Decimal("398.00"))

    def test_orderitem_str(self):
        item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            price=Decimal("199.00"),
        )
        self.assertIn("Teclado", str(item))


class ProductsViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        Product.objects.create(
            name="Produto A", slug="produto-a", price=Decimal("50.00"), sku="PA-001"
        )
        Product.objects.create(
            name="Produto B",
            slug="produto-b",
            price=Decimal("75.00"),
            sku="PB-001",
            available=False,
        )

    def test_lists_only_available_products(self):
        from shipping.views import ProductsView

        request = self.factory.get("/products/")
        response = ProductsView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data["products"]), 1)
        self.assertEqual(data["products"][0]["name"], "Produto A")


class CartViewTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Fone", slug="fone", price=Decimal("150.00"), sku="FN-001"
        )

    def test_add_item_to_cart(self):
        from django.test import Client

        client = Client()
        response = client.post(
            "/cart/",
            data=json.dumps({"product_id": self.product.pk, "quantity": 2}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["quantity"], 2)

    def test_add_nonexistent_product_returns_404(self):
        from django.test import Client

        client = Client()
        response = client.post(
            "/cart/",
            data=json.dumps({"product_id": 9999, "quantity": 1}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)


class OrdersViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="orderer", password="pass")
        Order.objects.create(user=self.user, total=Decimal("100.00"))

    def test_requires_authentication(self):
        from django.test import Client

        client = Client()
        response = client.get("/orders/")
        self.assertEqual(response.status_code, 401)

    def test_returns_user_orders(self):
        from django.test import Client

        client = Client()
        client.login(username="orderer", password="pass")
        response = client.get("/orders/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data["orders"]), 1)

