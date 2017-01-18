# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# © 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import openerp.tests.common as common
from openerp import fields
from datetime import datetime, timedelta


class TestDdmrp(common.TransactionCase):

    def createEstimatePeriod(self, name, date_from, date_to):
        data = {
            'name': name,
            'date_from': fields.Date.to_string(date_from),
            'date_to': fields.Date.to_string(date_to)
        }
        res = self.estimatePeriodModel.create(data)
        return res

    def setUp(self):
        super(TestDdmrp, self).setUp()

        # Models
        self.productModel = self.env['product.product']
        self.orderpointModel = self.env['stock.warehouse.orderpoint']
        self.pickingModel = self.env['stock.picking']
        self.quantModel = self.env['stock.quant']
        self.estimateModel = self.env['stock.demand.estimate']
        self.estimatePeriodModel = self.env['stock.demand.estimate.period']
        self.aducalcmethodModel = self.env['product.adu.calculation.method']
        self.locationModel = self.env['stock.location']

        # Refs
        self.main_company = self.env.ref('base.main_company')
        self.warehouse = self.env.ref('stock.warehouse0')
        self.stock_location = self.env.ref('stock.stock_location_stock')
        self.location_shelf1 = self.env.ref('stock.stock_location_components')
        self.supplier_location = self.env.ref('stock.stock_location_suppliers')
        self.customer_location = self.env.ref('stock.stock_location_customers')
        self.uom_unit = self.env.ref('product.product_uom_unit')
        self.buffer_profile_pur = self.env.ref(
            'ddmrp.stock_buffer_profile_replenish_purchased_short_low')

        self.productA = self.productModel.create(
            {'name': 'product A',
             'standard_price': 1,
             'type': 'product',
             'uom_id': self.uom_unit.id,
             'default_code': 'A',
             })

        self.binA = self.locationModel.create({
            'usage': 'internal',
            'name': 'Bin A',
            'location_id': self.location_shelf1.id,
            'company_id': self.main_company.id
        })

        self.quantModel.create(
            {'location_id': self.binA.id,
             'company_id': self.main_company.id,
             'product_id': self.productA.id,
             'qty': 200.0})

    def create_pickingoutA(self, date_move, qty):
        return self.pickingModel.create({
            'picking_type_id': self.ref('stock.picking_type_out'),
            'location_id': self.binA.id,
            'location_dest_id': self.customer_location.id,
            'move_lines': [
                (0, 0, {
                    'name': 'Test move',
                    'product_id': self.productA.id,
                    'date_expected': date_move,
                    'date': date_move,
                    'product_uom': self.productA.uom_id.id,
                    'product_uom_qty': qty,
                    'location_id': self.binA.id,
                    'location_dest_id': self.customer_location.id,
                })]
        })

    def test_adu_calculation_fixed(self):
        method = self.env.ref('ddmrp.adu_calculation_method_fixed')
        orderpointA = self.orderpointModel.create({
            'buffer_profile_id': self.buffer_profile_pur.id,
            'product_id': self.productA.id,
            'location_id': self.stock_location.id,
            'warehouse_id': self.warehouse.id,
            'product_min_qty': 0.0,
            'product_max_qty': 0.0,
            'qty_multiple': 0.0,
            'dlt': 10,
            'adu_calculation_method': method.id,
            'adu_fixed': 4
        })
        self.orderpointModel.cron_ddmrp()

        to_assert_value = 4
        self.assertEqual(orderpointA.adu, to_assert_value)

    def test_adu_calculation_past_120_days(self):

        method = self.env.ref('ddmrp.adu_calculation_method_past_120')
        orderpointA = self.orderpointModel.create({
            'buffer_profile_id': self.buffer_profile_pur.id,
            'product_id': self.productA.id,
            'location_id': self.stock_location.id,
            'warehouse_id': self.warehouse.id,
            'product_min_qty': 0.0,
            'product_max_qty': 0.0,
            'qty_multiple': 0.0,
            'dlt': 10,
            'adu_calculation_method': method.id,
            'adu_fixed': 4
        })
        self.orderpointModel.cron_ddmrp()

        self.assertEqual(orderpointA.adu, 0)

        pickingOuts = self.pickingModel
        date_move = datetime.today() - timedelta(days=30)
        pickingOuts += self.create_pickingoutA(date_move, 60)
        date_move = datetime.today() - timedelta(days=60)
        pickingOuts += self.create_pickingoutA(date_move, 60)
        for picking in pickingOuts:
            picking.action_confirm()
            picking.action_assign()
            picking.action_done()

        self.orderpointModel.cron_ddmrp()

        to_assert_value = (60 + 60) / 120
        self.assertEqual(orderpointA.adu, to_assert_value)

    def test_adu_calculation_future_120_days_actual(self):
        method = self.aducalcmethodModel.create({
            'name': 'Future actual demand (120 days)',
            'method': 'future',
            'use_estimates': False,
            'horizon': 120,
            'company_id': self.main_company.id
        })

        pickingOuts = self.pickingModel
        date_move = datetime.today() + timedelta(days=30)
        pickingOuts += self.create_pickingoutA(date_move, 60)
        date_move = datetime.today() + timedelta(days=60)
        pickingOuts += self.create_pickingoutA(date_move, 60)

        pickingOuts.action_confirm()

        orderpointA = self.orderpointModel.create({
            'buffer_profile_id': self.buffer_profile_pur.id,
            'product_id': self.productA.id,
            'location_id': self.stock_location.id,
            'warehouse_id': self.warehouse.id,
            'product_min_qty': 0.0,
            'product_max_qty': 0.0,
            'qty_multiple': 0.0,
            'dlt': 10,
            'adu_calculation_method': method.id
        })
        self.orderpointModel.cron_ddmrp()

        to_assert_value = (60 + 60) / 120
        self.assertEqual(orderpointA.adu, to_assert_value)

        # Create a move more than 120 days in the future
        date_move = datetime.today() + timedelta(days=150)
        pickingOuts += self.create_pickingoutA(date_move, 1)

        # The extra move should not affect to the average ADU
        self.assertEqual(orderpointA.adu, to_assert_value)

    def test_adu_calculation_future_120_days_estimated(self):

        method = self.env.ref('ddmrp.adu_calculation_method_future_120')
        # Create a period of 120 days.
        date_from = datetime.now().date()
        date_to = (datetime.now() + timedelta(days=119)).date()
        estimate_period_next_120 = self.createEstimatePeriod(
            'test_next_120', date_from, date_to)

        self.estimateModel.create({
            'period_id': estimate_period_next_120.id,
            'product_id': self.productA.id,
            'product_uom_qty': 120,
            'product_uom': self.productA.uom_id.id,
            'location_id': self.stock_location.id
        })

        orderpointA = self.orderpointModel.create({
            'buffer_profile_id': self.buffer_profile_pur.id,
            'product_id': self.productA.id,
            'location_id': self.stock_location.id,
            'warehouse_id': self.warehouse.id,
            'product_min_qty': 0.0,
            'product_max_qty': 0.0,
            'qty_multiple': 0.0,
            'dlt': 10,
            'adu_calculation_method': method.id
        })
        self.orderpointModel.cron_ddmrp()

        to_assert_value = 120 / 120
        self.assertEqual(orderpointA.adu, to_assert_value)

    def test_qualified_demand_1(self):
        """Moves within order spike horizon, outside the threshold but past
        or today's demand."""
        method = self.env.ref('ddmrp.adu_calculation_method_fixed')
        orderpointA = self.orderpointModel.create({
            'buffer_profile_id': self.buffer_profile_pur.id,
            'product_id': self.productA.id,
            'location_id': self.stock_location.id,
            'warehouse_id': self.warehouse.id,
            'product_min_qty': 0.0,
            'product_max_qty': 0.0,
            'qty_multiple': 0.0,
            'dlt': 10,
            'adu_calculation_method': method.id,
            'adu_fixed': 4,
            'adu': 4,
            'order_spike_horizon': 40
        })

        date_move = datetime.today()
        expected_result = orderpointA.order_spike_threshold * 2
        pickingOut1 = self.create_pickingoutA(
            date_move, expected_result)
        pickingOut1.action_confirm()
        self.orderpointModel.cron_ddmrp()
        self.assertEqual(orderpointA.qualified_demand, expected_result)

    def test_qualified_demand_2(self):
        """Moves within order spike horizon, below threshold. Should have no
        effect on the qualified demand."""
        method = self.env.ref('ddmrp.adu_calculation_method_fixed')
        orderpointA = self.orderpointModel.create({
            'buffer_profile_id': self.buffer_profile_pur.id,
            'product_id': self.productA.id,
            'location_id': self.stock_location.id,
            'warehouse_id': self.warehouse.id,
            'product_min_qty': 0.0,
            'product_max_qty': 0.0,
            'qty_multiple': 0.0,
            'dlt': 10,
            'adu_calculation_method': method.id,
            'adu_fixed': 4,
            'adu': 4,
            'order_spike_horizon': 40
        })

        date_move = datetime.today() + timedelta(days=10)
        self.create_pickingoutA(
            date_move, orderpointA.order_spike_threshold - 1)
        self.orderpointModel.cron_ddmrp()

        self.assertEqual(orderpointA.qualified_demand, 0)

    def test_qualified_demand_3(self):
        """Moves within order spike horizon, above threshold. Should have an
        effect on the qualified demand"""
        method = self.env.ref('ddmrp.adu_calculation_method_fixed')
        orderpointA = self.orderpointModel.create({
            'buffer_profile_id': self.buffer_profile_pur.id,
            'product_id': self.productA.id,
            'location_id': self.stock_location.id,
            'warehouse_id': self.warehouse.id,
            'product_min_qty': 0.0,
            'product_max_qty': 0.0,
            'qty_multiple': 0.0,
            'dlt': 10,
            'adu_calculation_method': method.id,
            'adu_fixed': 4,
            'adu': 4,
            'order_spike_horizon': 40
        })

        date_move = datetime.today() + timedelta(days=10)
        self.create_pickingoutA(date_move, orderpointA.order_spike_threshold
                                * 2)
        self.orderpointModel.cron_ddmrp()

        expected_result = orderpointA.order_spike_threshold * 2
        self.assertEqual(orderpointA.qualified_demand, expected_result)

    def test_qualified_demand_4(self):
        """ Moves outside of order spike horizon, above threshold. Should
        have no effect on the qualified demand"""
        method = self.env.ref('ddmrp.adu_calculation_method_fixed')
        orderpointA = self.orderpointModel.create({
            'buffer_profile_id': self.buffer_profile_pur.id,
            'product_id': self.productA.id,
            'location_id': self.stock_location.id,
            'warehouse_id': self.warehouse.id,
            'product_min_qty': 0.0,
            'product_max_qty': 0.0,
            'qty_multiple': 0.0,
            'dlt': 10,
            'adu_calculation_method': method.id,
            'adu_fixed': 4,
            'adu': 4,
            'order_spike_horizon': 40
        })


        date_move = datetime.today() + timedelta(days=100)
        self.create_pickingoutA(date_move, orderpointA.order_spike_threshold
                                * 2)
        self.orderpointModel.cron_ddmrp()

        expected_result = 0.0
        self.assertEqual(orderpointA.qualified_demand, expected_result)
