# -*- coding: utf-8 -*-
import base64
import uuid
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero
from odoo import api, fields, models, _


class SurveyBinary(models.Model):
    _name = 'survey.binary'

    user_input_line_id = fields.Many2one('survey.user_input.line', string="Answers")
    binary_filename = fields.Char(string="Upload File Name")
    binary_data = fields.Binary(string="Upload File Data")
    access_token = fields.Char(required=True, default=lambda x: uuid.uuid4().hex, index=False, copy=False)


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    def save_lines(self, question, answer, comment=None):
        old_answers = self.env['survey.user_input.line'].search([
            ('user_input_id', '=', self.id),
            ('question_id', '=', question.id)
        ])

        if question.question_type in ['char_box', 'text_box', 'numerical_box', 'date', 'datetime']:
            self._save_line_simple_answer(question, old_answers, answer)
            if question.save_as_email and answer:
                self.write({'email': answer})
            if question.save_as_nickname and answer:
                self.write({'nickname': answer})

        elif question.question_type in ['simple_choice', 'multiple_choice']:
            self._save_line_choice(question, old_answers, answer, comment)
        elif question.question_type == 'matrix':
            self._save_line_matrix(question, old_answers, answer, comment)
        elif question.question_type == 'upload_file':
            pass
        else:
            raise AttributeError(question.question_type + ": This type of question has no saving function")


class SurveyUserInputLine(models.Model):
    _inherit = "survey.user_input.line"

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

    @api.constrains('skipped', 'answer_type')
    def _check_answer_type_skipped(self):
        for line in self:
            if (line.skipped == bool(line.answer_type)):
                raise ValidationError(_('A question can either be skipped or answered, not both.'))

            # allow 0 for numerical box
            if line.answer_type == 'numerical_box' and float_is_zero(line['value_numerical_box'], precision_digits=6):
                continue
            if line.answer_type == 'suggestion':
                field_name = 'suggested_answer_id'
            elif line.answer_type == "upload_file":
                continue
            elif line.answer_type:
                field_name = 'value_%s' % line.answer_type
            else:  # skipped
                field_name = False

            if field_name and not line[field_name]:
                raise ValidationError(_('The answer must be in the right type'))
