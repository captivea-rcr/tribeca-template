# -*- coding: utf-8 -*-

from odoo import fields, models


class SurveyQuestion(models.Model):
    _inherit = 'survey.question'

    question_type = fields.Selection(selection_add=[('upload_file', 'Upload File')])
    upload_multiple_file = fields.Boolean('Upload Multiple File')

    def validate_upload_file(self, post, answer_tag):
        errors = {}

        # Empty answer to mandatory question
        if self.constr_mandatory and not post[answer_tag]:
            errors.update({answer_tag: self.constr_error_msg})
        return errors
