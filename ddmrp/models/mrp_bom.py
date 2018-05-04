# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from openerp import api, fields, models, _
from openerp.exceptions import UserError

_logger = logging.getLogger(__name__)


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    is_buffered = fields.Boolean(
        string="Buffered?", compute="_compute_is_buffered",
        help="True when the product has an DDMRP buffer associated.",
    )
    orderpoint_id = fields.Many2one(
        comodel_name='stock.warehouse.orderpoint', string='Orderpoint',
        compute="_compute_is_buffered",
    )
    dlt = fields.Float(
        string="Decoupled Lead Time (days)",
        compute="_compute_dlt",
    )
    has_mto_rule = fields.Boolean(
        string="MTO",
        help="Follows an MTO Pull Rule",
        compute="_compute_mto_rule",
    )
    has_mto_rule_exception = fields.Char(string="MTO Exception",
                                         compute="_compute_mto_rule",
                                         default=False)
    has_mto_rule_exception_msg = fields.Char(string="MTO Exception Message",
                                             compute="_compute_mto_rule")

    def _get_search_buffer_domain(self):
        product = self.product_id or \
            self.product_tmpl_id.product_variant_ids[0]
        domain = [('product_id', '=', product.id),
                  ('buffer_profile_id', '!=', False)]
        if self.location_id:
            domain.append(('location_id', '=', self.location_id.id))
        return domain

    def _compute_is_buffered(self):
        for bom in self:
            domain = bom._get_search_buffer_domain()
            orderpoint = self.env['stock.warehouse.orderpoint'].search(
                domain, limit=1)
            bom.orderpoint_id = orderpoint
            bom.is_buffered = True if orderpoint else False

    def _compute_mto_rule(self):
        for rec in self:
            product = rec.product_id or rec.product_tmpl_id
            try:
                mto_route = self.env['stock.warehouse']._get_mto_route()
            except:
                mto_route = False
            routes = product.route_ids + product.route_from_categ_ids
            # TODO: optimize with read_group?
            pulls = self.env['procurement.rule'].search(
                [('route_id', 'in', [x.id for x in routes]),
                 ('location_id', '=', rec.location_id.id),
                 ('location_src_id', '!=', False)])
            if len(pulls.mapped('procure_method')) > 1:
                rec.has_mto_rule_exception = True
                rec.has_mto_rule_exception_msg = _(
                    "This product has mixed Make to Stock / Make to Order "
                    "pull rules for the selected location.")
                rec.has_mto_rule = False
            if pulls and all(pm == 'make_to_order' for pm in pulls.mapped(
                    'procure_method')):
                rec.has_mto_rule = True
            elif not pulls:
                if mto_route and mto_route.id in [x.id for x in routes]:
                    rec.has_mto_rule = True
            else:  # There's some make_to_stock rule
                rec.has_mto_rule = False

    @api.multi
    def _get_longest_path(self):
        if not self.bom_line_ids:
            return 0.0
        paths = [0] * len(self.bom_line_ids)
        i = 0
        for line in self.bom_line_ids:
            if line.is_buffered:
                i += 1
            elif line.product_id.bom_ids:
                # If the a component is manufactured we continue exploding.
                location = line.location_id
                line_boms = line.product_id.bom_ids
                bom = line_boms.filtered(
                    lambda bom: bom.location_id == location) or \
                    line_boms.filtered(lambda bom: not bom.location_id)
                if bom:
                    produce_delay = bom[0].product_id.produce_delay or \
                        bom[0].product_tmpl_id.produce_delay
                    paths[i] += produce_delay
                    paths[i] += bom[0]._get_longest_path()
                else:
                    _logger.info(
                        "ddmrp (dlt): Product %s has no BOM for location "
                        "%s." % (line.product_id.name, location.name))
                i += 1
            else:
                # assuming they are purchased,
                if line.product_id.seller_ids:
                    paths[i] = line.product_id.seller_ids[0].delay
                else:
                    _logger.info(
                        "ddmrp (dlt): Product %s has no seller set." %
                        line.product_id.name)
                i += 1
        return max(paths)

    @api.multi
    def _get_manufactured_dlt(self):
        """Computes the Decoupled Lead Time exploding all the branches of the
        BOM until a buffered position and then selecting the greatest."""
        self.ensure_one()
        dlt = self.product_id.produce_delay or \
            self.product_tmpl_id.produce_delay
        dlt += self._get_longest_path()
        return dlt

    def _compute_dlt(self):
        for rec in self:
            rec.dlt = rec._get_manufactured_dlt()


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    is_buffered = fields.Boolean(
        string="Buffered?", compute="_compute_is_buffered",
        help="True when the product has an DDMRP buffer associated.",
    )
    orderpoint_id = fields.Many2one(
        comodel_name='stock.warehouse.orderpoint', string='Orderpoint',
        compute="_compute_is_buffered",
    )
    dlt = fields.Float(
        string="Decoupled Lead Time (days)",
        compute="_compute_dlt",
    )
    has_mto_rule = fields.Boolean(
        string="MTO",
        help="Follows an MTO Pull Rule",
        compute="_compute_mto_rule",
    )
    has_mto_rule_exception = fields.Char(string="MTO Exception",
                                         compute="_compute_mto_rule",
                                         default=False)
    has_mto_rule_exception_msg = fields.Char(string="MTO Exception Message",
                                             compute="_compute_mto_rule")

    def _get_search_buffer_domain(self):
        product = self.product_id or \
            self.product_tmpl_id.product_variant_ids[0]
        domain = [('product_id', '=', product.id),
                  ('buffer_profile_id', '!=', False)]
        if self.location_id:
            domain.append(('location_id', '=', self.location_id.id))
        return domain

    def _compute_is_buffered(self):
        for line in self:
            domain = line._get_search_buffer_domain()
            orderpoint = self.env['stock.warehouse.orderpoint'].search(
                domain, limit=1)
            line.orderpoint_id = orderpoint
            line.is_buffered = True if orderpoint else False

    def _compute_dlt(self):
        for rec in self:
            if rec.product_id.bom_ids:
                rec.dlt = rec.product_id.bom_ids[0].dlt
            else:
                rec.dlt = rec.product_id.seller_ids and \
                    rec.product_id.seller_ids[0].delay or 0.0

    def _compute_mto_rule(self):
        for rec in self:
            product = rec.product_id
            try:
                mto_route = self.env['stock.warehouse']._get_mto_route()
            except:
                mto_route = False
            routes = product.route_ids + product.route_from_categ_ids
            # TODO: optimize with read_group?
            pulls = self.env['procurement.rule'].search(
                [('route_id', 'in', [x.id for x in routes]),
                 ('location_id', '=', rec.location_id.id),
                 ('location_src_id', '!=', False)])
            if len(pulls.mapped('procure_method')) > 1:
                rec.has_mto_rule_exception = True
                rec.has_mto_rule_exception_msg = _(
                    "This product has mixed Make to Stock / Make to Order "
                    "pull rules for the selected location.")
                rec.has_mto_rule = False
            if pulls and all(pm == 'make_to_order' for pm in pulls.mapped(
                    'procure_method')):
                rec.has_mto_rule = True
            elif not pulls:
                if mto_route and mto_route.id in [x.id for x in routes]:
                    rec.has_mto_rule = True
            else:  # There's some make_to_stock rule
                rec.has_mto_rule = False

    @api.multi
    def action_mto_rule_exception(self):
        raise UserError(self.has_mto_rule_exception_msg)
