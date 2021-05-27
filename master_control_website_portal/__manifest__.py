# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Master Control Website Portal',
    'version': '1.0',
    'category': 'Website',
    'summary': 'This is used for display website portal view for Master Control.',
    'description': """
This module is used to display website portal view for Master Control.
======================================
This module used to display website portal view for Master Control.
    """,
    'depends': ['portal'],
    'data': [
        'views/master_control_portal_template.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
