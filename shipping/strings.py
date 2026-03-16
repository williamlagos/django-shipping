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

from django.utils.translation import gettext_lazy as _

# Correios service
CORREIOS_SERVICE_NAME = _("Correios")
CORREIOS_RESULTS_LABEL = _("Resultados:")
CORREIOS_ERRORS_LABEL = _("Erros:")
CORREIOS_INVALID_HTML = _("HTML recebido não é válido")

# FreteFacil validation errors
FRETEFACIL_HEIGHT_TOO_SMALL = _("Altura abaixo do mínimo (2cm).")
FRETEFACIL_WIDTH_TOO_SMALL = _("Largura abaixo do mínimo (11cm).")
FRETEFACIL_LENGTH_TOO_SMALL = _("Profundidade abaixo do mínimo (16cm).")
FRETEFACIL_CANNOT_CALCULATE = _("Não foi possível calcular o frete.")

# Shipping labels
SHIPPING_VALUE_LABEL = _("Valor do frete")
SHIPPING_SEDEX_LABEL = _("Frete via SEDEX")
SHIPPING_PRODUCT_NAME = _("Produto do Plethora")

# Order status choices
ORDER_STATUS_PENDING = _("Pendente")
ORDER_STATUS_PAID = _("Pago")
ORDER_STATUS_SHIPPED = _("Enviado")
ORDER_STATUS_DELIVERED = _("Entregue")
ORDER_STATUS_CANCELLED = _("Cancelado")
