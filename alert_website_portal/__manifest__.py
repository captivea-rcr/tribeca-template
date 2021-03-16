# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Alert Website Portal',
    'version': '1.0',
    'category': 'Website',
    'summary': 'This is used for display website portal view for alerts.',
    'description': """
This module is used to display website portal view for alerts.
======================================
This module used to display website portal view for alerts.
    """,
    'depends': ['portal'],
    'data': [
        'security/ir.model.access.csv',
        'views/alert_view.xml',
        'views/alert_portal_template.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
