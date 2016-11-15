# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# © 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class StockDemandEstimate(models.Model):
    _inherit = 'stock.demand.estimate'

    @api.multi
    @api.depends('product_id', 'location_id')
    def _compute_orderpoint_id(self):
        for rec in self:
            locations = self.env['stock.location'].search(
                [('parent_left', '<=', rec.location_id.parent_left),
                 ('parent_right', '>=', rec.location_id.parent_right)])
            orderpoints = self.env['stock.warehouse.orderpoint'].search(
                [('product_id', '=', rec.product_id.id),
                 ('location_id', 'in', locations.ids)])
            if orderpoints:
                rec.orderpoint_id = orderpoints[0]
            else:
                rec.orderpoint_id = False

    # We need the fields in order to properly store computed fields in the
    # orderpoints.
    orderpoint_id = fields.Many2one(
        comodel_name="stock.warehouse.orderpoint",
        string="Minimum stock rule", compute='_compute_orderpoint_id',
        store=True)

