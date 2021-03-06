# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author Adrien CHAUSSENDE <adrien.chaussende@akretion.com>
#  @author David BEAL <david.beal@akretion.com>
#
##############################################################################

from openerp.osv import orm, fields
from openerp import models, api
import simplejson


class SaleOrderLine(orm.Model):
    _inherit = 'sale.order.line'

    def _get_configuration(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = simplejson.dumps(line.config)
        return res

    def _set_configuration(self, cr, uid, ids, field_name, field_value, arg,
                           context=None):
        if isinstance(ids, int) or isinstance(ids, long):
            ids = [ids]
        for line in self.browse(cr, uid, ids, context=context):
            if not field_value:
                field_value = "{}"
            self.write(cr, uid, line.id, {
                field_name.replace('_text', ''): simplejson.loads(
                    field_value)}, context=context)
        return True

    def _check_product_data(self, cr, uid, product_data, context=None):
        product_ids = []
        for product in product_data:
            if 'product_id' not in product:
                return False
            if 'qty' in product:
                if not isinstance(product('qty'), (int, float)):
                    return False
            product_ids.append(product['product_id'])
        prd_ids = self.pool['product.product'].search(
            cr, uid, [['id', 'in', list(set(product_ids))]], context=context)
        if len(prd_ids) != product_ids:
            return False
        return True

    def is_correct_config(self, cr, uid, ids, context=None):
        # TODO check than final product_id is not the config
        assert len(ids) == 1, "is_correct_config() should only be used "
        "for a single id"
        sline = self.browse(cr, uid, ids[0], context=context)
        res = False
        if sline.product_id and sline.product_id.track_from_sale:
            if sline.config:
                product_data = sline.config.get('bom', False)
                if product_data:
                    res = self._check_product_data(product_data)
        return res

    _columns = {
        'config': fields.serialized(
            'Configuration',
            readonly=True,
            help="Allow to set custom configuration"),
        'config_text': fields.function(
            _get_configuration,
            fnct_inv=_set_configuration,
            type="text",
            string='Configuration'
        ),
        'lot_id': fields.many2one(
            'stock.production.lot',
            oldname='lot_id',
            string='Serial Number',
            readonly=True)
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['lot_id'] = False
        return super(SaleOrderLine, self).copy_data(
            cr, uid, id, default, context=context)

    _defaults = {
        'config': {'bom': [{'product_id': 5, 'qty': 3},
                {'product_id': 6, 'qty': 5}, {'product_id': 9},
                {'product_id': 4}]}
    }


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _prepare_sale_line(self, sale_line):
        """Prepare values to override sale line fields"""
        return {}

    @api.model
    def _prepare_vals_lot_number(self, order_line_id, index_lot):
        """Prepare values before creating a lot number"""
        order_line = self.env['sale.order.line'].browse(order_line_id)
        lot_number = "%s-%02d" % (order_line.order_id.name, index_lot)
        return {
            'name': lot_number,
            'product_id': order_line.product_id.id,
            # in V8 company_id doesn't exist
            #'company_id': order_line.order_id.company_id.id,
            'config': order_line.config,
        }

    @api.multi
    def action_ship_create(self):
        self.ensure_one()
        lot_m = self.env['stock.production.lot']
        for sale_order in self:
            index_lot = 1
            for line in sale_order.order_line:
                line_vals = {}
                if line.product_id.track_from_sale:
                    vals = self._prepare_vals_lot_number(
                        line.id, index_lot)
                    index_lot += 1
                    lot_id = lot_m.create(vals)
                    line_vals['lot_id'] = lot_id.id
                line_vals.update(self._prepare_sale_line(line))
                if line_vals:
                    line.write(line_vals)
        return super(SaleOrder, self).action_ship_create()

    @api.model
    def _prepare_order_line_move(self, order, line, picking_id, date_planned):
        """ original method is in module purchase/purchase.py """
        result = super(SaleOrder, self)._prepare_order_line_move(
            order, line, picking_id, date_planned)
        result.update({'lot_id': line.lot_id.id})
        return result
