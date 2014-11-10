# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) All Rights Reserved 2014 Akretion
#    @author Adrien CHAUSSENDE <adrien.chaussende@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.tests.common import TransactionCase

class BaseTest(TransactionCase):
    def setUp(self):
        super(BaseTest, self).setUp()
        self.product_obj = self.registry('product.product')
        self.sale_order_obj = self.registry('sale.order')
        self.order_line_obj = self.registry('sale.order.line')
        self.partner_obj = self.registry('res.partner')
        self.move_obj = self.registry('stock.move')
        self.order_line_obj = self.registry('sale.order.line')
        self.mrp_prod_obj = self.registry('mrp.production')
        self.bom_obj = self.registry('mrp.bom')


    def _init_products(self):
        cr, uid = self.cr, self.uid
        self.products = {}
        # Product 0 : Component of Product 1
        components = []
        vals_compo = {
            'name' : 'Component 1',
            'type' : 'product',
            'purchase_ok' : True,
            'procure_method' : 'make_to_stock',
            'supply_method' : 'buy',
            'track_from_sale' : False,
        }
        components.append(
            self.product_obj.create(cr, uid, vals_compo)
        )
        # Product 1 : Tracked product
        vals_1 = {
            'name' : 'Tracked product',
            'type' : 'product',
            'sale_ok' : True,
            'procure_method' : 'make_to_order',
            'supply_method' : 'produce',
            'track_from_sale' : True,
        }
        self.products[self.product_obj.create(cr, uid, vals_1)] = components

    def _init_partner_id(self):
        """Search for one partner which can be a customer"""
        cr, uid = self.cr, self.uid
        self.partner_id = self.partner_obj.search(
            cr, uid, [('customer','=','True')])[0]

    def _init_sale_order(self):
        """
            Create a sale order based on list of product ids that are contained
            in self. Uses _init_product_ids and _init_partner_id.
        """
        cr, uid = self.cr, self.uid
        #Create sale order_infos_keys
        order_infos = self.sale_order_obj.onchange_partner_id(
            cr, uid, [], self.partner_id
        )['value']
        vals_sale_order = {
            'partner_id': self.partner_id,
            'pricelist_id': order_infos['pricelist_id'],
            'partner_invoice_id': self.partner_obj.address_get(
                cr, uid, [self.partner_id], ['invoice']
            )['invoice'],
            'partner_shipping_id' : self.partner_obj.address_get(
                cr, uid, [self.partner_id], ['delivery']
            )['delivery'],
        }
        self.sale_order_id = self.sale_order_obj.create(
            cr, uid, vals_sale_order
        )
        #Sale order lines
        for product_id in self.products.keys():
            product = self.product_obj.browse(cr, uid, product_id)
            #Get some default values for product quantity
            product = self.move_obj.onchange_product_id(
                cr, uid, [], product_id
            )['value']
            order_line = self.order_line_obj.product_id_change(
                cr, uid, [], order_infos['pricelist_id'], product_id,
                product['product_qty'], partner_id=self.partner_id
            )['value']
            order_line['order_id'] = self.sale_order_id
            order_line['product_id'] = product_id
            order_line['configuration'] = {}
            self.order_line_obj.create(cr, uid, order_line)

    def _check_vals(self, dict_1, dict_2):
        dict2_keys = dict_2.keys()
        for key in dict_1.keys():
            self.assertIn(key, dict2_keys())
            self.assertEquals(
                dict_1[key], dict_2[key], "Bad value for key %s" % key
            )


class TestSuccess(BaseTest):
    def setUp(self):
        super(TestSuccess, self).setUp()
        self._init_products()
        self._init_partner_id()
        self._init_sale_order()

    def test_00_main_scenario(self):
        cr, uid = self.cr, self.uid
        # Sale Order confirm
        self.sale_order_obj.action_button_confirm(cr, uid, [self.sale_order_id])
        sale_order = self.sale_order_obj.browse(cr, uid, self.sale_order_id)
        mo_ids = self.mrp_prod_obj.search(
            cr, uid, [('sale_name','=',sale_order.name)]
        )
        mos = self.mrp_prod_obj.browse(cr, uid, mo_ids)
        for mo in mos:
            print {
                "id" : mo.id,
                "name" : mo.name,
                "sale_name" : mo.sale_name,
                "product_id.name" : mo.product_id.name,
            }

