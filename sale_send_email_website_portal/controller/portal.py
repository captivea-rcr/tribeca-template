# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerPortal(CustomerPortal):

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
        toString = lambda a : '' if not a else str(a)
        address = toString(sale_order.partner_id.street) + "," + toString(sale_order.partner_id.city) + "," + \
                  toString(sale_order.partner_id.state_id.name) + "," + toString(sale_order.partner_id.zip) + \
                  "," + toString(sale_order.partner_id.country_id.name)
        while ',,' in address:address=address.replace(',,',',')
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
