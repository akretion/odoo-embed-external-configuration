# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>
#
##############################################################################

from osv import orm



class StockMove(orm.Model):
    _inherit = 'stock.move'

    def _action_explode(self, cr, uid, move, context=None):
        processed_ids = super(StockMove, self)._action_explode(
            cr, uid, move, context=context)
        child_ids = list(processed_ids)
        move_master_id = child_ids.pop()
        move_master = self.browse(cr, uid, move_master_id, context=context)
        if move_master.product_id.track_from_sale:
            lot_index = 1
            for move in self.browse(cr, uid, child_ids, context=context):
                if move.product_id.track_from_sale:
                    vals = self._prepare_lot_for_move(
                        cr, uid, move, move_master, lot_index, context=context)
                    prodlot_id = self.pool['stock.production.lot'].create(
                        cr, uid, vals, context=context)
                    lot_index += 1
                    print vals, prodlot_id
                    move.write({'prodlot_id': prodlot_id})
        return processed_ids

    def _prepare_lot_for_move(
            self, cr, uid, move, move_master, lot_index, context=None):
        lot_number = "%s-%03d" % (
            move_master.sale_line_id.prodlot_id.name, lot_index)
        return {
            'name': lot_number,
            'product_id': move.product_id.id,
            'company_id': move_master.company_id.id,
            'config': move_master.prodlot_id.config,
        }
