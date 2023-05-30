# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################
{
    'name': 'Multiple Invoice Payment',
    'version': '15.0.1.0',
    'sequence': 1,
    'description': """
        App will allow multiple invoice payment from payment and invoice screen.
       Multiple invoice payment, Invoice Multiple payment, Payment , Partial Invoice Payment, Full invoice Payment,Payment write off,   Payment Invoice, 
    """,
    "category": 'Accounting',
    'summary': 'These apps use to easy payment multi invoice payment | multi-vendor bill payment mass invoice payment | mass bill payment | multiple invoice payment | multiple bill payment, multiple partial payment | multi-payment vendor bill | multiple payment vendor bills, multi invoice payment',
    'author': 'DevIntelle Consulting Service Pvt.Ltd', 
    'website': 'http://www.devintellecs.com',
    'depends': ['sale_management', 'account'],
    'data': [
            'security/ir.model.access.csv',
            'views/account_payment.xml',
            'wizard/bulk_invoice_payment.xml',
            ],
    'demo': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 35.0,
    'currency': 'EUR',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
