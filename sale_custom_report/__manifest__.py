# -*- coding: utf-8 -*-
{
    'name': "Format de devis personalisé",
    'description': """
        impression d'un timbre fiscal
    """,
    'author': "Ahmed Mnasri",
    'website': "http://polyline.xyz",
    'category': 'sale',
    'version': '1.0',
    'depends': ['sale',
                ],
    'data': [
        'report/report.xml',
        'views/sale_order_view.xml',
        'views/sale_report_templates.xml',
    ],
    'installable': True,
    'auto_install': False,
}
