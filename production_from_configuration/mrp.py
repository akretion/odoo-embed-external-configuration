# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>
#
##############################################################################

from osv import orm


class MrpProduction(orm.Model):
    """ Purpose to generate manufacturing base on custom product raw material
    """
    _inherit = 'mrp.production'

    def _get_product_from_config(
            self, cr, uid, production, product_data, context=None):
        return product_data

    def _action_compute_lines(
            self, cr, uid, ids, properties=None, context=None):
        if context is None:
            context = {}
        res = {}
        for production in self.browse(cr, uid, ids, context=context):
            context.update({'production': production})
            res = super(MrpProduction, self)._action_compute_lines(
                cr, uid, ids, properties=properties, context=context)
        return res


class MrpBom(orm.Model):
    _inherit = 'mrp.bom'

    def _bom_explode(
            self, cr, uid, bom, factor, properties=None, addthis=False,
            level=0, routing_id=False, context=None):
        prod_m = self.pool['mrp.production']
        if context is None:
            context = {}
        product_data, workcenter_data = super(
            MrpBom, self)._bom_explode(
                cr, uid, bom, factor, properties=properties, addthis=addthis,
                level=level, routing_id=routing_id, context=context)
        production = context.get('production', False)
        if production:
            new_product_data = prod_m._get_product_from_config(
                cr, uid, production, product_data, context=context)
            del product_data
            product_data = list(new_product_data)
        return product_data, workcenter_data
