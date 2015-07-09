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

    def _init_product_ids(self):
        """Will create 2 products from scratch"""
        cr, uid = self.cr, self.uid
        self.product_ids = []
        # Product 1 : Track product
        vals_1 = {
            'name' : 'Tracked product',
            'type' : 'product',
            'sale_ok' : True,
            'procure_method' : 'make_to_order',
            'supply_method' : 'produce',
            'auto_generate_prodlot' : True,
        }
        self.product_ids.append(
            self.product_obj.create(cr, uid, vals_1)
        )
        # Product 2 : Untracked product
        vals = {
            'name' : 'Untracked product',
            'type' : 'product',
            'sale_ok' : True,
            'purchase_ok' : True,
            'procure_method' : 'make_to_order',
            'supply_method' : 'produce',
            'auto_generate_prodlot' : False,
        }
        self.product_ids.append(
            self.product_obj.create(cr, uid, vals)
        )

        #Product 3 : Another Tracked Product
        self.product_ids.append(
            self.product_obj.create(cr, uid, vals_1)
        )

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
        for product_id in self.product_ids:
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


class TestSuccess(BaseTest):
    def setUp(self):
        super(TestSuccess, self).setUp()
        self._init_product_ids()
        self._init_partner_id()
        self._init_sale_order()

    def test_main_scenario(self):
        cr, uid = self.cr, self.uid
        self.sale_order_obj.action_button_confirm(
            cr, uid, [self.sale_order_id]
        )
        sale_order = self.sale_order_obj.browse(
            cr, uid, self.sale_order_id
        )

        index_lot = 1
        for line in sale_order.order_line:
            if line.lot_id:
                lot_number = "%s-%03d" % (
                    line.order_id.name, index_lot)
                self.assertEquals(
                    line.lot_id.name, lot_number, "Invalid prodlot number"
                )
                index_lot += 1
        self.assertNotIn(
            sale_order.state, ['draft','cancel'], "Bad sale order state"
        )
        for picking in sale_order.picking_ids:
            self.assertEquals(
                len(picking.move_lines), len(sale_order.order_line),
                "Not enough moves created for the picking"
            )
            for move_line in picking.move_lines:
                if move_line.lot_id :
                    line = self.order_line_obj.browse(
                        cr, uid, move_line.sale_line_id.id
                    )
                    self.assertEquals(
                        move_line.lot_id.name, line.lot_id.name,
                        "Invalid transfered production lot name. Must be\
                        the same name on move line and sale order line"
                    )
