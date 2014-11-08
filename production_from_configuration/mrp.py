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

    def _get_product_from_configuration(
            self, cr, uid, procurement_id, product_data, context=None):
        return product_data

    def make_mo(self, cr, uid, ids, context=None):
        result = {}
        for procurement in self.pool['procurement.order'].browse(
                cr, uid, ids, context=context):
            context.update({'procurement': procurement.id})
            res = super(MrpProduction, self).make_mo(
                cr, uid, [procurement.id], context=context)
            result.append(res)
        return result

    def _bom_explode(
            self, cr, uid, bom, factor, properties=None, addthis=False,
            level=0, routing_id=False, context=None):
        product_data, workcenter_data = super(
            MrpProduction, self)._bom_explode(
                cr, uid, bom, factor, properties=properties, addthis=addthis,
                level=level, routing_id=routing_id, context=context)
        procurement_id = context.get('procurement', False)
        if procurement_id:
            self._get_product_from_configuration(
                cr, uid, procurement_id, product_data, context=context)
        return product_data, workcenter_data
