# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    @api.multi
    @api.depends('product_stock_location_ids',
                 'product_stock_location_ids.'
                 'product_location_qty_available_not_res'
                 )
    def _compute_product_location_qty_available_not_res(self):
        for rec in self:
            for psl in self.env['product.stock.location'].search(
                    [('orderpoint_id', '=', rec.id)]):
                rec.product_location_qty_available_not_res = \
                    psl.product_location_qty_available_not_res

    product_location_qty_available_not_res = fields.Float(
        compute='_compute_product_location_qty_available_not_res',
        store='True')
