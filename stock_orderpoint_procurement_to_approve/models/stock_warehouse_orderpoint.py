# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp.addons import decimal_precision as dp
from openerp import api, fields, models

UNIT = dp.get_precision('Product Unit of Measure')


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    @api.model
    def _get_to_approve_qty(self, procurement):
        """Method to obtain the quantity to approve. We assume that by
        default all stock pickings are approved. We focus on purchase orders"""
        uom_obj = self.env['product.uom']
        qty = uom_obj._compute_qty_obj(
            procurement.product_uom,
            procurement.product_qty,
            procurement.product_id.uom_id)
        return qty

    @api.multi
    def _compute_procured_pending_approval_qty(self):
        for rec in self:
            to_approve_qty = 0.0
            procurements = self.env['procurement.order'].search(
                [('location_id', '=', rec.location_id.id),
                 ('product_id', '=', rec.product_id.id),
                 ('to_approve', '=', True)])
            for procurement in procurements:
                to_approve_qty += self._get_to_approve_qty(procurement)
            rec.to_approve_qty = to_approve_qty

    to_approve_qty = fields.Float(
        string='Procured pending approval',
        compute="_compute_procured_pending_approval_qty",
        digits=UNIT)
