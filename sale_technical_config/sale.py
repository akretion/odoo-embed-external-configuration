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


class sale_order_line(orm.Model):
    _inherit = 'sale.order.line'
    _columns = {
        'technical_config': fields.text(
            'Technical Configuration',
            help="Allow to set custom configuration with json like notation")
    }

