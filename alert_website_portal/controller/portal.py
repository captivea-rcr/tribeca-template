# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.portal.controllers.portal import pager as portal_pager, CustomerPortal
from odoo.osv.expression import OR


class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        values['alert_count'] = request.env['x_alert'].search_count([])
        if values.get('sales_user', False):
            values['title'] = _("Salesperson")
        return values

    def _alert_get_page_view_values(self, alert_id, access_token, **kwargs):
        values = {
            'page_name': 'x_alert',
            'alert_id': alert_id,
        }
        return self._get_page_view_values(alert_id, access_token, values, 'alert_history', False, **kwargs)

    @http.route(['/my/alerts', '/my/alerts/page/<int:page>'], type='http', auth="user", website=True)
    def my_alert(self, page=1, date_begin=None, date_end=None, sortby=None, search=None, search_in='content', **kw):
        values = self._prepare_portal_layout_values()
        user = request.env.user
        domain = []

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'subject': {'label': _('Subject'), 'order': 'subject'},
        }
        searchbar_inputs = {
            'content': {'input': 'content', 'label': _('Search <span class="nolabel"> (in Content)</span>')},
            'customer': {'input': 'subject', 'label': _('Search in Subject')},
            'id': {'input': 'id', 'label': _('Search ID')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('id', 'all'):
                search_domain = OR([search_domain, [('id', '=', search)]])
            if search_in in ('content', 'all'):
                search_domain = OR([search_domain, ['|', ('body_html', 'ilike', search), ('subject', 'ilike', search)]])
            if search_in in ('subject', 'all'):
                search_domain = OR([search_domain, [('subject', 'ilike', search)]])
            domain += search_domain

        # pager
        alert_count = request.env['x_alert'].search_count(domain)
        pager = portal_pager(
            url="/my/alert",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=alert_count,
            page=page,
            step=self._items_per_page
        )

        alert = request.env['x_alert'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['alert_history'] = alert.ids[:100]

        values.update({
            'date': date_begin,
            'alerts': alert,
            'page_name': 'Alert',
            'default_url': '/my/alert',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'sortby': sortby,
            'search_in': search_in,
            'search': search,
        })
        return request.render("alert_website_portal.portal_alert", values)

    @http.route([
        "/my/alert/<int:alert_id>",
        "/my/alert/<int:alert_id>/<access_token>",
    ], type='http', auth="public", website=True)
    def alert_followup(self, alert_id=None, access_token=None, **kw):
        alert_sudo = request.env['x_alert'].sudo().browse(alert_id)
        values = self._alert_get_page_view_values(alert_sudo, access_token, **kw)
        return request.render("alert_website_portal.alert_followup", values)
