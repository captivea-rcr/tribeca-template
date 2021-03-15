# -*- coding: utf-8 -*-
import json
import base64

import odoo.http as http
from odoo.http import request

from odoo.addons.survey.controllers.main import Survey

class Survey(Survey):

    @http.route(
        ["/web/binary/download/<int:file_id>"],
        type='http', auth="public", website=True, sitemap=False)
    def binary_download(self, file_id=None, **post):
        if file_id:
            binary_file = request.env['survey.binary'].browse([file_id])
            if binary_file:
                status, headers, content = request.env['ir.http'].binary_content(model='survey.binary', id=binary_file.id, field='binary_data', filename_field=binary_file.binary_filename)
                content_base64 = base64.b64decode(content) if content else ''
                headers.append(('Content-Type', 'application/octet-stream'))
                headers.append(('Content-Length', len(content_base64)))
                headers.append(('Content-Disposition', 'attachment; filename=' + binary_file.binary_filename + ';'))
                return request.make_response(content_base64, headers)
        return False

    @http.route('/survey/submit/<string:survey_token>/<string:answer_token>', type='http', methods=['POST'], auth='public', website=True)
    def survey_submit(self, survey_token, answer_token, **post):
        access_data = self._get_access_data(survey_token, answer_token, ensure_token=True)
        if access_data['validity_code'] is not True:
            return {}

        survey_sudo, answer_sudo = access_data['survey_sudo'], access_data['answer_sudo']
        if survey_sudo.questions_layout == 'page_per_section':
            page_id = int(post['page_id'])
            questions = request.env['survey.question'].sudo().search([('survey_id', '=', survey_sudo.id), ('page_id', '=', page_id)])
            questions = questions & answer_sudo.question_ids
        elif survey_sudo.questions_layout == 'page_per_question':
            question_id = int(post['question_id'])
            questions = request.env['survey.question'].sudo().browse(question_id)
        else:
            questions = survey_sudo.question_ids
            questions = questions & answer_sudo.question_ids

        for question in questions.filtered((lambda question: question.question_type == 'upload_file')):
            answer_tag = "%s_%s" % (survey_sudo.id, question.id)
            post[answer_tag] = request.httprequest.files.getlist(answer_tag)
        return super(Survey, self).survey_submit(survey_token, answer_token, **post)

    @http.route('/survey/prefill/<string:survey_token>/<string:answer_token>', type='http', auth='public', website=True)
    def survey_get_answers(self, survey_token, answer_token, page_or_question_id=None, **post):
        json_prefill = super(Survey, self).survey_get_answers(survey_token, answer_token, page_or_question_id=page_or_question_id, **post)

        if 'file_mode' in post and post.get('file_mode') == 'true':
            access_data = self._get_access_data(survey_token, answer_token, ensure_token=True)
            if access_data['validity_code'] is not True and access_data['validity_code'] != 'answer_done':
                return {}

            survey_sudo, answer_sudo = access_data['survey_sudo'], access_data['answer_sudo']
            try:
                page_or_question_id = int(page_or_question_id)
            except:
                page_or_question_id = None

            # Fetch previous answers
            if survey_sudo.questions_layout == 'one_page' or not page_or_question_id:
                previous_answers = answer_sudo.user_input_line_ids
            elif survey_sudo.questions_layout == 'page_per_section':
                previous_answers = answer_sudo.user_input_line_ids.filtered(lambda line: line.page_id.id == page_or_question_id)
            else:
                previous_answers = answer_sudo.user_input_line_ids.filtered(lambda line: line.question_id.id == page_or_question_id)

            ret = {}
            for answer in previous_answers:
                if not answer.skipped:
                    answer_tag = '%s_%s' % (answer.survey_id.id, answer.question_id.id)
                    answer_value = None
                    if answer.answer_type == 'upload_file':
                        answer_value = [("/web/binary/download/%s" % (file.id), file.binary_filename) for file in answer.user_binary_line]
                        if answer_value:
                            ret.setdefault(answer_tag, []).append(answer_value)

            json_prefill = json.loads(json_prefill.get_data().decode('utf-8'))
            json_prefill.update(ret)
            return json.dumps(json_prefill, default=str)
        return json_prefill
