# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests import common


class TestProductStockLocationAvailableUnreserved(common.TransactionCase):

    def setUp(self):
        super(TestProductStockLocationAvailableUnreserved, self).setUp()
        # Get required Model
        self.product_stock_location_model = self.env['product.stock.location']
        self.product_model = self.env['product.product']
        self.product_ctg_model = self.env['product.category']
        self.stock_location_model = self.env['stock.location']

        # Get required Model data
        self.product_uom = self.env.ref('product.product_uom_unit')
        self.location_stock = self.env.ref('stock.stock_location_stock')
        self.location_shelf1 = self.env.ref('stock.stock_location_components')
        self.location_customer = self.env.ref('stock.stock_location_customers')
        self.location_supplier = self.env.ref('stock.stock_location_suppliers')
        self.location_chicago = self.env.ref('stock.stock_location_shop0')

        # Create product category and product
        self.product_ctg = self._create_product_category()
        self.product = self._create_product()

        # Create a stock location
        self.location_bin1 = self._create_stock_location()
        self.stock_location_model._parent_store_compute()

    def _create_product_category(self):
        """Create a Product Category."""
        product_ctg = self.product_ctg_model.create({
            'name': 'test_product_ctg',
            'type': 'normal',
        })
        return product_ctg

    def _create_product(self):
        """Create a Stockable Product."""
        product = self.product_model.create({
            'name': 'Test Product',
            'categ_id': self.product_ctg.id,
            'type': 'product',
            'uom_id': self.product_uom.id,
        })
        return product

    def _create_stock_location(self):
        """Create a Stock Location."""
        location = self.stock_location_model.create({
            'name': 'Test bin location',
            'usage': 'internal',
            'location_id': self.location_shelf1.id,
        })
        return location

    def create_move(self, source_location, destination_location):
        move = self.env['stock.move'].create({
            'name': 'Test move',
            'product_id': self.product.id,
            'product_uom': self.product_uom.id,
            'product_uom_qty': 10,
            'location_id': source_location.id,
            'location_dest_id': destination_location.id}
        )

        move.action_confirm()
        return move

    def test_product_qty(self):
        """Tests the product quantity in the locations"""
        # Create & process moves to test the product quantity
        move_in_1 = self.create_move(self.location_supplier,
                                     self.location_bin1)
        move_out_1 = self.create_move(self.location_bin1,
                                      self.location_customer)

        psl_bin1 = self.product_stock_location_model.search(
            [('product_id', '=', self.product.id),
             ('location_id', '=', self.location_bin1.id)])
        psl_shelf1 = self.product_stock_location_model.search(
            [('product_id', '=', self.product.id),
             ('location_id', '=', self.location_shelf1.id)])
        psl_stock = self.product_stock_location_model.search(
            [('product_id', '=', self.product.id),
             ('location_id', '=', self.location_stock.id)])

        # Check WH/Stock/Shelf 1/Bin 1
        self.assertEqual(psl_bin1.product_location_qty_available_not_res,
                         0, 'On Hand Qty (Unreserved) does not match')
        # Check WH/Stock/Shelf 1
        self.assertEqual(psl_shelf1.product_location_qty_available_not_res,
                         0, 'On Hand Qty (Unreserved) does not match')
        # Check WH/Stock
        self.assertEqual(psl_stock.product_location_qty_available_not_res,
                         0, 'On Hand Qty (Unreserved) does not match')

        # Move in 1
        move_in_1.action_done()

        # Check WH/Stock/Shelf 1/Bin 1
        self.assertEqual(psl_bin1.product_location_qty_available_not_res,
                         10, 'On Hand Qty (Unreserved) does not match')
        # Check WH/Stock/Shelf 1
        self.assertEqual(psl_shelf1.product_location_qty_available_not_res,
                         10, 'On Hand Qty (Unreserved) does not match')
        # Check WH/Stock
        self.assertEqual(psl_stock.product_location_qty_available_not_res,
                         10, 'On Hand Qty (Unreserved) does not match')

        # Move out 1
        move_out_1.action_assign()
        # Check WH/Stock/Shelf 1/ Bin 1
        self.assertEqual(psl_bin1.product_location_qty_available_not_res,
                         0, 'On Hand Qty (Unreserved) does not match')
        # Check WH/Stock/Shelf 1
        self.assertEqual(psl_shelf1.product_location_qty_available_not_res,
                         0, 'On Hand Qty (Unreserved) does not match')
        # Check WH/Stock
        self.assertEqual(psl_stock.product_location_qty_available_not_res,
                         0, 'On Hand Qty (Unreserved) does not match')
