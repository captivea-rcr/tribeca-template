# -*- coding: utf-8 -*-
import base64

from odoo import api, fields, models

class SurveyBinary(models.Model):
    _name = 'survey.binary'

    user_input_line_id = fields.Many2one('survey.user_input.line', string="Answers")
    binary_filename = fields.Char(string="Upload File Name")
    binary_data = fields.Binary(string="Upload File Data")

class SurveyUserInputLine(models.Model):
    _inherit = "survey.user_input_line"

    user_binary_line = fields.One2many('survey.binary', 'user_input_line_id', string='Binary Files')
    answer_type = fields.Selection(selection_add=[('upload_file', 'Upload File')])

    @api.model
    def save_line_upload_file(self, user_input_id, question, post, answer_tag):
        vals = {
            'user_input_id': user_input_id,
            'question_id': question.id,
            'survey_id': question.survey_id.id,
            'skipped': False,
        }
        if answer_tag in post:
            if post[answer_tag] != '':
                user_binary_lines = [
                    (0, 0, {'binary_data': base64.encodestring(u_file.read()), 'binary_filename': u_file.filename})
                    for u_file in post[answer_tag]
                ]
                vals.update({'answer_type': 'upload_file', 'user_binary_line': user_binary_lines})
        else:
            vals.update({'answer_type': None, 'skipped': True})
        old_uil = self.search([
            ('user_input_id', '=', user_input_id),
            ('survey_id', '=', question.survey_id.id),
            ('question_id', '=', question.id)
        ])
        if old_uil:
            old_uil.write(vals)
        else:
            old_uil.create(vals)
        return True
