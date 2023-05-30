# -*- coding: utf-8 -*-

{
    'name': 'Alternative to Odoo.sh for Odoo Community',
    'summary': 'Manage Repositories.',
    'version': '15.0.1.0.0',
    'category': 'Hidden',
    #'category': 'Extra Tools',
    'website': "https://odoonext.com/",
    'author': 'David Montero Crespo',
    'installable': True,
    'external_dependencies': {'python': ['GitPython']}, # Docker instances fails at subprocess.check_call(["python3", "-m", "pip", "install", 'GitPython'])
    'depends': [
        'base','mail'
    ],
    'data': [
        'data/data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/repository_repository_view.xml',
        'views/panel_tool.xml',
        'views/ir_module_module.xml',
        'views/upload_module.xml',
        'wizard/installer.xml'
    ],
    'application': False,
    'price': 100,
    "uninstall_hook": "uninstall_hook",
    'images': ['static/description/imagen.png'],
    'currency': 'EUR',
    'license': 'AGPL-3',
}
