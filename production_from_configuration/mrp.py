# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>
#
##############################################################################

from osv import orm, fields


class mrp_production(orm.Model):
    """
    Purpose to generate manufacturing base on custom product raw material
    """
    _inherit = 'mrp.production'

    _columns = {
        'sale_line': fields.many2one('sale.order.line','Sale Line'),
        #'on_subcontract': fields.boolean('On Subcontract?'),
        #'serial_number': fields.related('soline_subcontract', 'serial_number', type='char', relation='sale.order.line', string='Serial Number', store=True),
        #'custom_bom_component': fields.text('Custom BoM Components', readonly=True),
        #'tech_description': fields.text('Custom BoM Components', readonly=True),
        #'table_tech_description': fields.html('Technical Description', readonly=True, states={'draft': [('readonly', False)]}),
        #'manufacture_order_id': fields.char('Manufacture Order ID', size=200)
    }
