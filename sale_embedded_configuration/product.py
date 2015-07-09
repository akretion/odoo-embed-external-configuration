# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author Adrien CHAUSSENDE <adrien.chaussende@akretion.com>
#
##############################################################################

from openerp import models, fields
from openerp.osv import orm, fields as oldfields


class StockProductionLot(orm.Model):
    _inherit = 'stock.production.lot'

    _columns = {
        'config': oldfields.serialized(
            'Configuration',
            readonly=True,
            help="Allow to set custom configuration")
    }
