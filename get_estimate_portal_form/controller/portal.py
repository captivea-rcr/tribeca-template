# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.portal.controllers.portal import pager as portal_pager, CustomerPortal
from odoo.osv.expression import OR


class CustomerPortal(CustomerPortal):

    @http.route(["/estimate-thank-you", ], type='http', auth="public", website=True)
    def estimate_thank_you(self, **kw):
        get_estimate_survey = request.env['survey.survey'].search([('title', '=', 'Get Estimate')])
        survey = request.env['survey.user_input'].search([('survey_id', '=', get_estimate_survey.id)], limit=1, order='id desc')
        values = {
            'survey': survey,
        }
        return request.render("get_estimate_portal_form.estimate_thanks", values)
