# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>
#
##############################################################################

from openerp import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    lot_name = fields.Char(
        help="Customized lot number")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _prepare_vals_lot_number(self, order_line_id, index_lot):
        """Prepare values before creating a lot number"""
        res = super(SaleOrder, self)._prepare_vals_lot_number(
            order_line_id, index_lot)
        order_line = self.env['sale.order.line'].browse(order_line_id)
        if order_line.lot_name:
            res['name'] = order_line.lot_name
        return res
