# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Procurement to approve",
    "summary": "Shows the procurements pending to be converted to "
               "confirmed purchase orders",
    "version": "8.0.1.0.0",
    "author": "Eficent Business and IT Consulting Services S.L,"
              "Odoo Community Association (OCA)",
    "website": "https://www.odoo-community.org",
    "category": "Warehouse Management",
    "depends": ["purchase"],
    "data": ["views/procurement_order_view.xml"],
    "license": "AGPL-3",
    'installable': True,
    'application': False,
}
