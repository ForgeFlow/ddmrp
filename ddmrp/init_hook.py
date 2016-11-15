# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# © 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

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
    store_field_orderpoint_id(cr)
    store_field_orderpoint_dest_id(cr)


def store_field_orderpoint_id(cr):
    cr.execute(
        """
        ALTER TABLE stock_move ADD COLUMN orderpoint_id integer;
        COMMENT ON COLUMN stock_move.orderpoint_id IS 'Origin Orderpoint';
        """)

    logger.info('Computing field orderpoint_id on stock.move')

    cr.execute(
        """
        UPDATE stock_move sm
        SET orderpoint_id = op.id
        FROM stock_warehouse_orderpoint as op
        WHERE op.product_id = sm.product_id
        AND sm.location_id in (
            SELECT sl.id
            FROM stock_location as sl
            INNER JOIN stock_location as sl2
            ON sl2.id = op.location_id
            WHERE sl.parent_left <= sl2.parent_left
            AND sl.parent_right >= sl2.parent_right
            LIMIT 1)
        """
    )


def store_field_orderpoint_dest_id(cr):

    cr.execute(
        """
        ALTER TABLE stock_move ADD COLUMN orderpoint_dest_id integer;
        COMMENT ON COLUMN stock_move.orderpoint_dest_id IS 'Destination
        Orderpoint';
        """)

    logger.info('Computing field orderpoint_dest_id on stock.move')

    cr.execute(
        """
        UPDATE stock_move sm
        SET orderpoint_dest_id = op.id
        FROM stock_warehouse_orderpoint as op
        WHERE op.product_id = sm.product_id
        AND sm.location_dest_id in (
            SELECT sl.id
            FROM stock_location as sl
            INNER JOIN stock_location as sl2
            ON sl2.id = op.location_id
            WHERE sl.parent_left <= sl2.parent_left
            AND sl.parent_right >= sl2.parent_right
            LIMIT 1)
        """
    )
