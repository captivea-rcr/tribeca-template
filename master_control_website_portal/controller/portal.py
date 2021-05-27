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
        values['master_control_count'] = request.env['x_master_control'].search_count([])
        if values.get('sales_user', False):
            values['title'] = _("Salesperson")
        return values

    def _master_control_get_page_view_values(self, master_control_id, access_token, **kwargs):
        values = {
            'page_name': 'Master Control',
            'master_control_id': master_control_id,
        }
        return self._get_page_view_values(master_control_id, access_token, values, 'master_control_history', False, **kwargs)

    @http.route(['/my/master_control', '/my/master_control/page/<int:page>'], type='http', auth="user", website=True)
    def my_master_control(self, page=1, date_begin=None, date_end=None, sortby=None, search=None, search_in='name', **kw):
        values = self._prepare_portal_layout_values()
        user = request.env.user
        domain = []

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'x_date desc'},
            'name': {'label': _('Name'), 'order': 'x_name'},
        }
        searchbar_inputs = {
            'name': {'input': 'name', 'label': _('Search <span class="nolabel"> (in Name)</span>')},
            'customer': {'input': 'customer', 'label': _('Search in customer')},
            'appointment': {'input': 'appointment', 'label': _('Search in Appointment')},
            's_user_input': {'input': 's_user_input', 'label': _('Search in Survey User Input')},
            'id': {'input': 'id', 'label': _('Search ID')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('x_date', '>', date_begin), ('x_date', '<=', date_end)]

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('id', 'all'):
                search_domain = OR([search_domain, [('id', '=', search)]])
            if search_in in ('customer', 'all'):
                search_domain = OR([search_domain, [('x_partner_id', '=', search)]])
            if search_in in ('appointment', 'all'):
                search_domain = OR([search_domain, [('x_appointment_id', '=', search)]])
            if search_in in ('customer', 'all'):
                search_domain = OR([search_domain, [('x_survey_user_input_id', '=', search)]])
            if search_in in ('name', 'all'):
                search_domain = OR([search_domain, [('x_name', 'ilike', search)]])
            domain += search_domain

        # pager
        master_control_count = request.env['x_master_control'].search_count(domain)
        pager = portal_pager(
            url="/my/master_control",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=master_control_count,
            page=page,
            step=self._items_per_page
        )

        master_control = request.env['x_master_control'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['master_control_history'] = master_control.ids[:100]

        values.update({
            'date': date_begin,
            'master_controls': master_control,
            'page_name': 'Master Control',
            'default_url': '/my/master_control',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'sortby': sortby,
            'search_in': search_in,
            'search': search,
        })
        return request.render("master_control_website_portal.portal_master_control", values)

    @http.route([
        "/my/master_control/<int:master_control_id>",
        "/my/master_control/<int:master_control_id>/<access_token>",
    ], type='http', auth="public", website=True)
    def master_control_followup(self, master_control_id=None, access_token=None, **kw):
        master_control_sudo = request.env['x_master_control'].sudo().browse(master_control_id)
        values = self._master_control_get_page_view_values(master_control_sudo, access_token, **kw)
        return request.render("master_control_website_portal.master_control_followup", values)
