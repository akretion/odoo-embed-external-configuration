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

from osv import orm, fields


class SaleOrderLine(orm.Model):
    _inherit = 'sale.order.line'

    def _get_configuration(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = simplejson.dumps(line.configuration)
        return res

    def _set_configuration(self, cr, uid, ids, field_name, field_value, arg,
                           context=None):
        res = {}
        if isinstance(ids, int) or isinstance(ids, long):
            ids = [ids]
        for line in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, line.id,
                {field_name.replace('_text', ''): simplejson.loads(field_value)},
                context=context)
        return True

    _columns = {
        'technical_config': fields.text(
            'Technical Configuration',
            help="Allow to set custom configuration with json like notation"),
        'configuration': fields.serialized('Configuration', readonly=True),
        'config_text': fields.function(
            _get_configuration,
            fnct_inv=_set_configuration,
            type="text",
            string='Configuration'
        ),
        'prodlot_id': fields.many2one(
            'stock.production.lot', 'Serial Number', readonly=True
        )
    }


class sale_order(orm.Model):
    _inherit = 'sale'

    def _prepare_vals_lot_number(cr, uid, order_line_id, index_lot, context=None):
        order_line = self.pool.get('sale.order.line').browse(
            cr, uid, order_line_id
        )
        lot_number = "%s-%03d" % (order_line.order_id.order_name, index_lot + 1)
        return {
            'name' : lot_number,
            'product_id' : order_line.product_id.id,
            'company_id' : order_line.order_id.company_id.id,
        }

    def action_button_confirm(cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        mod_prodlot = self.pool.get('stock.production.lot')
        sale_order = self.browse(cr, uid, ids, context=context)
        index_lot = 1
        for line in sale_order.order_line:
            if line.product_id.product_tmpl_id.track_from_order:
                vals = self._prepare_vals_lot_number(
                    cr, uid, line.id, index_lot, context=context
                )
                prodlot_id = mod_prodlot.create(
                    cr, uid, vals
                )
                line.write({'prodlot_id' : prodlot_id})
                index_lot += 1
        return super(sale_order, self).action_button_confirm(
            cr, uid, ids, context=context
        )


class ProductTemplate(orm.Model):
    _inherit = 'product.template'

    _columns = {
        'track_from_order' : fields.boolean(
            'Track Lots since Sale Order',
            help='Forces to specifiy a Serial Number for all moves containing\
            this product since the confirm of the Sale Order'
        )
    }
