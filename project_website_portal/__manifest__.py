# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Project Website Portal',
    'version': '1.0',
    'category': 'Website',
    'author': 'Captivea LLC.',
    'website': 'http://captivea.com',
    'summary': 'This is used for display website portal view for Job Photos in Task and Project Portal view.',
    'description': """
This module is used to display a job photos on website portal view for Project/Tasks.
======================================
This module is used to display a job photos on website portal view for Project/Tasks.
    """,
    'depends': ['portal', 'project'],
    'data': [
        'views/project_portal_template.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
