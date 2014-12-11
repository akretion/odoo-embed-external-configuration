# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>
#
##############################################################################

from openerp.osv import orm


class MrpProduction(orm.Model):
    """ Purpose to generate manufacturing base on custom product raw material
    """
    _inherit = 'mrp.production'
    _service_product_lst = []
    _product_config_dict = {}
    #'config': {'bom': [{'product_id': 5, 'qty': 3},
    #        {'product_id': 6, 'qty': 5}, {'product_id': 4}]}
#[{'workcenter_id': 1, 'cycle': 1.0, 'name': u'first - fab1', 'hour': 0.0, 'sequence': 0}, {'workcenter_id': 2, 'cycle': 1.0, 'name': u'second - fab1', 'hour': 0.0, 'sequence': 0}]

    def _put_note_in_manuf_order(
            self, cr, uid, product, context=None):
        return "Product: %s" % (product.name)

    def _put_bom_datas(self, cr, uid, product, context=None):
        return {
            'name': product.name,
            'product_id': product.id,
            'product_qty': self._product_config_dict[product.id]['qty'],
            'product_uom': product.uom_id.id,
            'product_uos_qty': False,
            'product_uos': False,
        }

    def _get_mrp_data_from_config(
            self, cr, uid, production, product_data, context=None):
        config = production.move_prod_id.procurement_id.sale_line_id.config
        if not config:
            return []
        config_product_data = []
        for product in self.pool['product.product'].browse(
                cr, uid, self._product_config_dict.keys(), context=context):
            if product.type in ('product', 'consu'):
                config_product_data.append(
                    self._put_bom_datas(cr, uid, product, context=context))
            else:
                self._service_product_lst.append(product.id)
        return config_product_data

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

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        move_obj = self.pool['stock.move']
        notes = []
        config = self.pool['stock.move'].browse(
            cr, uid, [vals['move_prod_id']],
            context=context).procurement_id.sale_line_id.config
        for product in config['bom']:
            self._product_config_dict[product['product_id']] = {
                'qty': product.get('qty', 1.0)}
        for product in self.pool['product.product'].browse(
                cr, uid, self._product_config_dict.keys(), context=context):
            note = self._put_note_in_manuf_order(
                cr, uid, product, context=context)
            if note:
                notes.append(note)
        if notes:
            vals['notes'] = ' - %s' % '\n<br> - '.join(notes)
        if 'move_prod_id' in vals:
            move = move_obj.browse(
                cr, uid, vals['move_prod_id'], context=context)
            vals['name'] = move.procurement_id.sale_line_id.lot_id.name
        return super(MrpProduction, self).create(
            cr, uid, vals, context=context)

    def _make_production_produce_line(self, cr, uid, production, context=None):
        if context is None:
            context = {}
        ctx = context.copy()
        ctx['default_lot_id'] = production.move_prod_id.procurement_id.sale_line_id.id
        return super(MrpProduction, self)._make_production_produce_line(
            cr, uid, production, context=ctx)


class MrpBom(orm.Model):
    _inherit = 'mrp.bom'

    def _bom_explode(
            self, cr, uid, bom, product, factor, properties=None,
            level=0, routing_id=False, context=None):
        prod_m = self.pool['mrp.production']
        if context is None:
            context = {}
        product_data, workcenter_data = super(
            MrpBom, self)._bom_explode(
                cr, uid, bom, product, factor, properties=properties,
                level=level, routing_id=routing_id, context=context)
        production = context.get('production', False)
        if production:
            new_product_data = prod_m._get_mrp_data_from_config(
                cr, uid, production, product_data, context=context)
            del product_data
            product_data = list(new_product_data)
        return product_data, workcenter_data


class ProcurementOrder(orm.Model):
    _inherit = 'procurement.order'

    def make_mo(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        context.update({'production_from_procurement': True})
        return super(ProcurementOrder, self).make_mo(
            cr, uid, ids, context=context)

