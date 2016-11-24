# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# © 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp.addons.ddmrp.init_methods import init_methods
import logging
logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    """
    The objective of this hook is to speed up the installation
    of the module on an existing Odoo instance.

    Without this script, if a database has a few hundred thousand
    moves, which is not unlikely, the update will take
    at least a few hours.
    """
    init_methods.store_field_orderpoint_id(cr)
    init_methods.store_field_orderpoint_dest_id(cr)
    init_methods.update_product_stock_location(cr)
