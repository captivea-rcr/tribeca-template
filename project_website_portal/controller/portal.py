# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.portal.controllers.portal import pager as portal_pager, CustomerPortal
from odoo.osv.expression import OR


class CustomerPortal(CustomerPortal):

    def _job_photo_get_page_view_values(self, job_photo_id, access_token, **kwargs):
        values = {
            'page_name': 'Job Photo',
            'job_photo_id': job_photo_id,
        }
        return self._get_page_view_values(job_photo_id, access_token, values, 'job_photo_history', False, **kwargs)

    @http.route([
        "/job_photo/<int:job_photo_id>",
        "/job_photo/<int:job_photo_id>/<access_token>",
    ], type='http', auth="public", website=True)
    def job_photo_followup(self, job_photo_id=None, access_token=None, **kw):
        job_photo_sudo = request.env['x_job_photos'].sudo().browse(job_photo_id)
        values = self._job_photo_get_page_view_values(job_photo_sudo, access_token, **kw)
        return request.render("project_website_portal.job_photos_followups", values)
