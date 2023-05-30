# -*- coding: utf-8 -*-
{
    'name': "Nati Partner Access Rules",
    'summary': """
      access rules for contact """,

    'description': """
      how to show and access to contact for sales user
      """,

    'author': "Mali, MuhlhelITS",
    'website': "http://muhlhel.com",
    'price': 0.50,
    'currency': 'USD',
    'license': 'OPL-1',
    'version': '14.0.0.0',
    'category': 'Sale',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['base','account',],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/res_groups.xml',
        'views/res_partner.xml',
        'views/res_groups.xml',
        'wizards/res_partner_access.xml',

    ],
    'images': ['static/description/banner.png'],
    'installable': True,
}
