# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product Stock Location Available Unreserved",
    "version": "8.0.1.0.0",
    "depends": [
        "product_stock_location",
        "stock_warehouse_orderpoint_stock_info_unreserved"
    ],
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "website": "http://www.eficent.com",
    "category": "Warehouse",
    "license": "AGPL-3",
    "data": [
        "views/product_stock_location_view.xml"
    ],
    'pre_init_hook': 'pre_init_hook',
    "installable": True,
    "auto_install": False,
}
