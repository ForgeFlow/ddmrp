# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from .stock_warehouse_orderpoint import _PRIORITY_LEVEL


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    ddmrp_comment = fields.Text(string="Follow-up Notes")


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def create(self, vals):
        record = super(PurchaseOrderLine, self).create(vals)
        record._calc_execution_priority()
        return record

    @api.multi
    @api.depends("product_id", "order_id.origin", "orderpoint_id")
    def _compute_orderpoint_id(self):
        for rec in self:
            if rec.order_id.origin and not rec.orderpoint_id:
                group_name = rec.order_id.origin.split(", ")[-1]
                if group_name != '':
                    group_id = self.env['procurement.group'].\
                        search([('name', '=', group_name)])
                    if group_id:
                        orderpoint_id = \
                            self.env['stock.warehouse.orderpoint'].\
                            search([('product_id', '=', rec.product_id.id),
                                    ('group_id', '=', group_id.id)], limit=1)
                            rec.orderpoint_id = orderpoint_id

    @api.multi
    def _calc_execution_priority(self):
        prods = self.filtered(
            lambda r: r.orderpoint_id and r.state not in ['done', 'cancel'])
        for rec in prods:
            rec.execution_priority_level = \
                rec.orderpoint_id.execution_priority_level
            rec.on_hand_percent = rec.orderpoint_id.on_hand_percent
        (self - prods).write({
            'execution_priority_level': None,
            'on_hand_percent': None,
        })

    orderpoint_id = fields.Many2one(compute='_compute_orderpoint_id',
                                    store=True, index=True, readonly=True)
    execution_priority_level = fields.Selection(
        string="Buffer On-Hand Status Level",
        selection=_PRIORITY_LEVEL, readonly=True,
    )
    on_hand_percent = fields.Float(
        string="On Hand/TOR (%)", readonly=True,
    )
    ddmrp_comment = fields.Text(related="order_id.ddmrp_comment")
