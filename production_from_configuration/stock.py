# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>
#
##############################################################################

from openerp.osv import orm


class StockMove(orm.Model):
    _inherit = 'stock.move'

    #Complicated code that explode the prodlot number
    #base function are really ugly, hard to inherit
    def _action_explode(self, cr, uid, move, context=None):
        if context is None:
            context = {}
        ctx = context.copy()
        ctx['prodlot_base_name'] = move.restrict_lot_id.name
        ctx['prodlot_index'] = 1
        ctx['explode_prodlot'] = True

        return super(StockMove, self)._action_explode(
            cr, uid, move, context=ctx)

    def _prepare_explode_move(self, cr, uid, move, line, context=None):
        product_obj = self.pool['product.product']
        prodlot_obj = self.pool['stock.production.lot']
        if context is None:
            context = {}
        res = super(StockMove, self).\
            _prepare_explode_move(cr, uid, move, line, context=context)
        if context.get('explode_prodlot'):
            if move.product_id.track_from_sale:
                product = product_obj.browse(
                    cr, uid, line['product_id'], context=context)
                if product.track_from_sale:
                    prodlot_vals = self._prepare_lot_for_move(
                        cr, uid, line['product_id'], move, context['prodlot_index'],
                        context=context)
                    res['restrict_lot_id'] = prodlot_obj.create(
                        cr, uid, prodlot_vals, context=context)
                    context['prodlot_index'] += 1
        return res

    def _prepare_lot_for_move(
            self, cr, uid, product_id, move, lot_index, context=None):
        lot_number = "%s-%03d" % (
            move.restrict_lot_id.name, lot_index)
        return {
            'name': lot_number,
            'product_id': product_id,
            'company_id': move.company_id.id,
            'config': move.restrict_lot_id.config,
        }

    def create_chained_picking(self, cr, uid, moves, context=None):
        new_moves = super(StockMove, self).create_chained_picking(
            cr, uid, moves, context=context)
        for new_move in new_moves:
            if new_move.move_dest_id.restrict_lot_id:
                new_move.write({
                    'restrict_lot_id': new_move.move_dest_id.restrict_lot_id.id,
                    })
        return new_moves
