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
from openerp import models, api


#[{'workcenter_id': 1, 'cycle': 1.0, 'name': u'first - fab1', 'hour': 0.0, 'sequence': 0}, {'workcenter_id': 2, 'cycle': 1.0, 'name': u'second - fab1', 'hour': 0.0, 'sequence': 0}]


class MrpProduction(models.Model):
    """ Purpose to generate manufacturing base on custom product raw material
    """
    _inherit = 'mrp.production'
    _service_product_lst = []
    _product_config_dict = {}

    def _format_note_in_manuf_order(self, product):
        return False

    def _put_bom_datas(self, product):
        return {
            'name': product.name,
            'product_id': product.id,
            'product_qty': self._product_config_dict[product.id]['qty'],
            'product_uom': product.uom_id.id,
            'product_uos_qty': False,
            'product_uos': False,
        }

    @api.model
    def _get_mrp_data_from_config(self, production, product_data):
        config = production.move_prod_id.procurement_id.sale_line_id.config
        if not config:
            return []
        config_product_data = []
        for product in self.env['product.product'].browse(
                self._product_config_dict.keys()):
            if product.type in ('product', 'consu'):
                config_product_data.append(
                    self._put_bom_datas(product))
            else:
                self._service_product_lst.append(product.id)
        return config_product_data

    @api.multi
    def _action_compute_lines(self, properties=None):
        res = []
        for production in self:
            self = self.with_context(production=production)
            res = super(MrpProduction, self)._action_compute_lines(
                properties=properties)
        return res

    @api.model
    def create(self, vals):
        move_obj = self.env['stock.move']
        notes = []
        move = self.env['stock.move'].browse([vals['move_prod_id']])
        config = move.procurement_id.sale_line_id.config
        if config:
            for product in config['bom']:
                self._product_config_dict[product['product_id']] = {
                    'qty': product.get('qty', 1.0)}
            for product in self.env['product.product'].browse(
                    self._product_config_dict.keys()):
                if product.type == 'service':
                    note = self._format_note_in_manuf_order(product)
                    if note:
                        notes.append(note)
            if notes:
                vals['notes'] = ' - %s' % '\n<br> - '.join(notes)
        if 'move_prod_id' in vals:
            move = move_obj.browse(vals['move_prod_id'])
            vals['name'] = move.procurement_id.sale_line_id.lot_id.name
        return super(MrpProduction, self).create(vals)


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.model
    def _bom_explode(self, bom, product, factor, properties=None, level=0,
                     routing_id=False, previous_products=None,
                     master_bom=None):
        prod_m = self.env['mrp.production']
        product_data, workcenter_data = super(
            MrpBom, self)._bom_explode(
                bom, product, factor, properties=properties,
                level=level, routing_id=routing_id,
                previous_products=previous_products, master_bom=master_bom)
        production = False
        if 'production' in self.env.context:
            production = self.env.context['production']
        if production:
            new_product_data = prod_m._get_mrp_data_from_config(
                production, product_data)
            del product_data
            product_data = list(new_product_data)
        return product_data, workcenter_data

