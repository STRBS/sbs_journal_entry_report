# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
from email.utils import formataddr
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @property
    def analytic_distribution_str(self):
        return ', '.join(
            ['%s: %s%%' % (
                self.env['account.analytic.account'].browse(int(k)).name,
                round(v, 2)
            ) for k, v in self.analytic_distribution.items()]
        ) if self.analytic_distribution else ''

    @property
    def tax_names_str(self):
        return ', '.join(self.tax_ids.mapped('name')) if self.tax_ids else ''


class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'mail.thread']

    ref = fields.Char(tracking=True)
    date = fields.Date(tracking=True)

    def button_cancel(self):
        res = super().button_cancel()
        for move in self:
            move.message_post(body=_('Journal Entry cancelled.'))
        return res

    # def _get_default_from(self):
    #     if self.env.user.email:
    #         return formataddr((self.env.user.name, self.env.user.email))
    #     raise UserError(_("Unable to send email, please configure the sender's email address or alias."))
    #
    # def create_mail_message(self, body):
    #     user = self.env.user
    #     for move in self:
    #         vals = {'message_type': 'notification',
    #                 'author_id': user.partner_id.id,
    #                 'date': datetime.now(),
    #                 'email_from': self._get_default_from(),
    #                 'model': 'account.move',
    #                 'res_id': move.id,
    #                 'subtype_id': 2,
    #                 'body': body}
    #         self.env['mail.message'].create(vals)


