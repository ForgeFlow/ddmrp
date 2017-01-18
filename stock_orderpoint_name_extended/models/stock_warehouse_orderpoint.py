# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    @api.multi
    def name_get(self):
        """Use the company name and template as name."""
        if 'name_show_extended' in self.env.context:
            res = []
            for orderpoint in self:
                name = orderpoint.name
                if orderpoint.product_id.default_code:
                    name += " [%s]" % orderpoint.product_id.default_code
                name += " %s" % orderpoint.product_id.name
                name += " - %s" % orderpoint.warehouse_id.name
                name += " - %s" % orderpoint.location_id.name
                res.append((orderpoint.id, name))
            return res
        return super(StockWarehouseOrderpoint, self).name_get()
