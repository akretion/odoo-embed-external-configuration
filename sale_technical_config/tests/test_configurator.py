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
from openerp.tests import common

class BaseTest(TransactionCase):
    def setUp(self):
        super(BaseTest, self).setUp()
        self.mod_product = self.registry('product.product')
        self.mod_sale_order = self.registry('sale.order')
        self.mod_order_line = self.registry('sale.order.line')

    def _init_product_ids(self):
        """ Will create 3 products from scratch """
        cr, uid, context = self.cr, self.uid, self.context
        # Product 1 : Track product
        vals = {
            'name' : 'Tracked product',
            'type' : 'product',
            'sale_ok' : True,
            'procure_method' : 'make_to_order',
            'supply_method' : 'produce',
            'product_tmpl_id.track_from_order' : True
        }
        product_id_1 = self.mod_product.create(cr, uid, vals, context=context)
        # Product 2 : Untracked product
        vals = {
            'name' : 'Tracked product',
            'type' : 'product',
            'sale_ok' : True,
            'purchase_ok' : True,
            'procure_method' : 'make_to_order',
            'supply_method' : 'produce',
            'product_tmpl_id.track_from_order' : False
        }
        product_id_2 = self.mod_product.create(cr, uid, vals, context=context)
