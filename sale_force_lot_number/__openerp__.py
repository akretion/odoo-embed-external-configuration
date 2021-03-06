# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Akretion (http://www.akretion.com).
#    @author Adrien CHAUSSENDE <adrien.chaussende@akretion.com>
#    @author David BEAL <david.beal@akretion.com>
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
##############################################################################


{
    'name': 'Sale Force Lot Number',
    'version': '0.5',
    'category': 'Generic Modules',
    'description': """
        Allows to customize lot number
    """,
    'author': 'Akretion',
    'website': 'http://akretion.com',
    'depends': [
        'sale_embedded_configuration',
    ],
    'data': [
        'sale_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
