# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    """
    The objective of this hook is to speed up the installation
    of the module on an existing Odoo instance.
    """
    update_product_stock_location(cr)


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
