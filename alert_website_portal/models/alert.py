# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class XAlert(models.Model):
    _name = 'x_alert'
    _inherits = {'mail.mail': 'mail_id'}
    _rec_name = "subject"

    mail_id = fields.Many2one("mail.mail", "Mail")
