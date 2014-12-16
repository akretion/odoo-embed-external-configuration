# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>
#
##############################################################################

from openerp import models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _format_note_in_manuf_order(self, product):
        super(MrpProduction, self)._format_note_in_manuf_order(product)
        return "Product: %s  Qty: %s" % (
               product.name, self._product_config_dict[product.id]['qty'])
