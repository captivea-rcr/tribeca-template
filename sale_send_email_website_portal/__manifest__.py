# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Sale order Send Email Website Portal',
    'version': '1.0',
    'category': 'Website',
    'author': 'Captivea LLC.',
    'website': 'http://captivea.com',
    'summary': 'This is used for display a button on sale order website portal view for send email to the customer.',
    'description': """
This module is used to Send Email from sale order portal view.
======================================
This module is used to Send Email from sale order portal view.
    """,
    'depends': ['portal', 'sale'],
    'data': [
        'views/sale_portal_template.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
