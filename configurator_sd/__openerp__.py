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


{
    'name': 'Technical Configuration for Stores Discount',
    'version': '1.0',
    'category': 'Generic Modules',
    'description': """
        Implements specific technical configuration for Stores Discount
    """,
    'author': 'Akretion',
    'website': '',
    'depends': [
        'sale_base_configurator', 'mrp_base_configurator',
        'purchase_base_configurator'
    ],
    'data': ['sale_view.xml'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
