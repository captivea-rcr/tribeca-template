# -*- coding: utf-8 -*-
{
    "name": "Survey File Upload Field",
    "summary": "Survey Multi File Upload Field and upload in attachment",
    "description": "Survey Multi File Upload Field and upload in attachment",

    'author': 'iPredict IT Solutions Pvt. Ltd.',
    'website': 'http://ipredictitsolutions.com',
    'support': 'ipredictitsolutions@gmail.com',

    'category': 'Survey',
    'version': '13.0.0.1.1',
    "depends": ["survey"],

    "data": [
        "security/ir.model.access.csv",
        "views/assets.xml",
        "views/survey_question_views.xml",
        "views/survey_user_input_line_views.xml",
        "views/survey_templates.xml",
    ],

    'license': "OPL-1",
    'price': 11,
    'currency': "EUR",

    "auto_install": False,
    "installable": True,

    'images': ['static/description/main.png'],
}
