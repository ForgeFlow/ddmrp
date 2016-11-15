# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Orderpoint Procurement to approve",
    "summary": "Shows the procurements to approve in the orderpoints",
    "version": "8.0.1.0.0",
    "author": "Eficent Business and IT Consulting Services S.L,"
              "Odoo Community Association (OCA)",
    "website": "https://www.odoo-community.org",
    "category": "Warehouse Management",
    "depends": ["procurement_to_approve",
                "stock"],
    "data": ["views/stock_warehouse_orderpoint_view.xml"],
    "license": "AGPL-3",
    'installable': True,
    'application': False,
}
