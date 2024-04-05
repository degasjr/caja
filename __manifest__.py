# -*- coding: utf-8 -*-
{
    'name': "Caja",

    'summary': """
        Este módulo fue creado para llevar el control de las finanzas personales
    """,

    'description': "",

    'author': "Alexis Adam",
    'website': "https://www.github.com/degasjr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'mail',
        'uom',
    ],

    # always loaded
    'data': [
        'data/00_empresa.xml',
        'data/bancos.xml',
        'security/grupos.xml',
        'security/ir.model.access.csv',
        'views/00_herencia.xml',
        'views/banco.xml',
        'views/concepto.xml',
        'views/impuesto.xml',
        'views/movimiento.xml',
        'views/proveedor.xml',
        'views/tag.xml',
        'views/tasa.xml',
        'views/menus.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
    'sequence': 0,
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
