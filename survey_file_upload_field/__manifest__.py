# -*- coding: utf-8 -*-
{
    "name": "Survey File Upload Field",
    "summary": "Survey Multi File Upload Field and upload in attachment",
    "description": "Survey Multi File Upload Field and upload in attachment",

    'author': 'Captivea LLC.',
    'website': 'http://captivea.com',

    'category': 'Survey',
    'version': '14.0.0.0.1',
    "depends": ["survey"],

    "data": [
        "security/ir.model.access.csv",
        "views/assets.xml",
        "views/survey_question_views.xml",
        "views/survey_user_input_line_views.xml",
        "views/survey_templates.xml",
    ],

    "auto_install": False,
    "installable": True,

}
