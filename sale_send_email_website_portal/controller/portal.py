# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager


class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        SaleOrder = request.env['sale.order']
        if 'quotation_count' in counters:
            if partner.customer_rank > 0:
                values['quotation_count'] = SaleOrder.search_count([
                    ('partner_id', '=', partner.id),
                    ('state', 'in', ['sent', 'cancel']),
                ]) if SaleOrder.check_access_rights('read', raise_exception=False) else 0
            else:
                values['quotation_count'] = SaleOrder.search_count([
                    ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
                    ('state', 'in', ['draft', 'sent', 'cancel']),
                ]) if SaleOrder.check_access_rights('read', raise_exception=False) else 0
        if 'order_count' in counters:
            values['order_count'] = SaleOrder.search_count([
                ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
                ('state', 'in', ['sale', 'done'])
            ]) if SaleOrder.check_access_rights('read', raise_exception=False) else 0

        return values

    @http.route(['/my/quotes', '/my/quotes/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_quotes(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']

        if partner.customer_rank > 0:
            domain = [
                ('partner_id', '=', partner.id),
                ('state', 'in', ['sent', 'cancel']),
            ]
        else:
            domain = [
                ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
                ('state', 'in', ['draft', 'sent', 'cancel']),
            ]

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        quotation_count = SaleOrder.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/quotes",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=quotation_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        quotations = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_quotations_history'] = quotations.ids[:100]

        values.update({
            'date': date_begin,
            'quotations': quotations.sudo(),
            'page_name': 'quote',
            'pager': pager,
            'default_url': '/my/quotes',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("sale.portal_my_quotations", values)

    @http.route(["/sale/send_email/<int:sale_id>"], type='http', auth="public", website=True)
    def sale_send_email(self, sale_id=None, **kw):
        sale_order = request.env['sale.order'].sudo().browse(sale_id)
        template_id = request.env['mail.template'].sudo().search([
            ('name', '=', 'Send Quote Estimate'), ('model_id.model', '=', 'sale.order')])
        ctx = {
            'default_model': 'sale.order',
            'default_res_id': sale_id,
            'default_use_template': bool(template_id.id),
            'default_template_id': template_id.id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
        }
        address = sale_order.partner_id.street + "," + sale_order.partner_id.city + "," + \
                  sale_order.partner_id.state_id.name + "," + sale_order.partner_id.zip + \
                  "," + sale_order.partner_id.country_id.name
        body = """
        Dear Customer,<br/><br/>

Thank You for choosing TriBeCa Flooring, Your premier turn-key Wood Flooring Solution. Attached you will find the estimates for '{0}' for your review.<br/><br/>

Please contact us with any questions or comments regarding your estimates.We are a pay-as-you-go service business.<br/><br/>

Please contact us with your payment when you are ready to schedule your job. CREDIT CARD PAYMENTS ARE SUBJECT TO A 3% document processing fee.<br/><br/>

All jobs may commence a minimum of 36 hours after your payment was received and/or 36 hours after materials have been delivered, when applicable.<br/><br/>

We look forward to working with you.<br/><br/>

Thank You. Good Day.
        """.format(address)
        vals = {
            'partner_ids': [(6, 0, [sale_order.partner_id.id])],
            'subject': "Tribeca Order (Ref %s)" % sale_order.name,
            'body': body,
        }
        mail_wizard = request.env['mail.compose.message'].with_context(ctx).create(vals)
        mail_wizard.sudo().action_send_mail()
        return request.redirect("/my/orders/%s" % sale_id)
