# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# © 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging
from ddmrp.init_methods import init_methods

_logger = logging.getLogger(__name__)

__name__ = "Upgrade to 8.0.2.0.0"


def migrate(cr, version):
    if not version:
        return
    init_methods.store_field_orderpoint_id(cr)
    init_methods.store_field_orderpoint_dest_id(cr)
