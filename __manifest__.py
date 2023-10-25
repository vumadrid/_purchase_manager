# -*- coding: utf-8 -*-
{
    'name': "purchase_manager",

    'summary': """
        Purchase_manager""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        'data/purchase_request_data.xml',
        'views/purchase_request.xml',
        'views/purchase_request_line.xml',
        'views/purchase_department.xml',
        # 'report/purchase_details_template.xml',
        # 'report/purchase_card.xml',
        # 'report/report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
