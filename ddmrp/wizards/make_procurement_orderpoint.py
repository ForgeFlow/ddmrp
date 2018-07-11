# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, api


class MakeProcurementOrderpoint(models.TransientModel):

    _inherit = 'make.procurement.orderpoint'

    @api.multi
    def make_procurement(self):
        """Refresh buffer after making procurement"""
        res = super().make_procurement()
        for item in self.item_ids:
            item.orderpoint_id.cron_actions()
        return res
