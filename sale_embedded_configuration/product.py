# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author Adrien CHAUSSENDE <adrien.chaussende@akretion.com>
#
##############################################################################

from openerp.osv import orm, fields


class ProductTemplate(orm.Model):
    _inherit = 'product.template'

    _columns = {
        'track_from_sale': fields.boolean(
            'Track Lots since Sale Order',
            help="Forces to specifiy a Serial Number for all "
                 "moves containing this product since the confirm "
                 "of the Sale Order"
        )
    }


class StockProductionLot(orm.Model):
    _inherit = 'stock.production.lot'

    _columns = {
        'config': fields.serialized(
            'Configuration',
            readonly=True,
            help="Allow to set custom configuration"),
    }
