# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# © 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

logger = logging.getLogger(__name__)


def store_field_orderpoint_id(cr):

    cr.execute("""SELECT column_name
    FROM information_schema.columns
    WHERE table_name='stock_move' AND
    column_name='orderpoint_id'""")
    if not cr.fetchone():
        logger.info('Adding field orderpoint_id to table stock_move')
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

    cr.execute("""SELECT column_name
    FROM information_schema.columns
    WHERE table_name='stock_move' AND
    column_name='orderpoint_dest_id'""")
    if not cr.fetchone():
        logger.info('Adding field orderpoint_dest_id to table stock_move')
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


def update_product_stock_location(cr):

    cr.execute("""SELECT column_name
    FROM information_schema.columns
    WHERE table_name='product_stock_location' AND
    column_name='product_location_qty_available_not_res'""")
    if not cr.fetchone():
        logger.info('Extending table product_stock_location with column '
                    'product_location_qty_available_not_res')
        cr.execute(
            """
            ALTER TABLE product_stock_location
            ADD COLUMN product_location_qty_available_not_res
            float;
            COMMENT ON COLUMN
            product_stock_location.product_location_qty_available_not_res IS
            'Quantity On Location (Unreserved)';
            """)

    logger.info('Updating product_location_qty_available_not_res '
                'in product_stock_location')

    cr.execute("""
        WITH quant_query AS (
            SELECT psl2.id, sum(sq.qty) as quantity
            FROM product_stock_location as psl2
            INNER JOIN stock_quant as sq
            ON sq.product_id = psl2.product_id
            INNER JOIN stock_location as sl_sq
            ON sq.location_id = sl_sq.id
            INNER JOIN stock_location as sl_psl
            ON psl2.location_id = sl_psl.id
            WHERE sl_sq.parent_left >= sl_psl.parent_left
            AND sl_sq.parent_right <= sl_psl.parent_right
            AND sq.reservation_id IS NULL
            GROUP BY psl2.id
        )

        UPDATE product_stock_location as psl1
        SET product_location_qty_available_not_res = qq.quantity,
        virtual_location_qty = qq.quantity
        FROM product_stock_location as psl2
        INNER JOIN quant_query AS qq
        ON qq.id = psl2.id
        WHERE psl1.id = psl2.id
    """)
