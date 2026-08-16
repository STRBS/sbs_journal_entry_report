# -*- coding: utf-8 -*-
from odoo import models, fields, _


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
    # account.move already inherits mail.thread through
    # mail.thread.main.attachment in core, so re-declaring it here added
    # nothing. What this module actually contributes is tracking on the two
    # fields below and the cancellation note.
    _inherit = 'account.move'

    ref = fields.Char(tracking=True)
    date = fields.Date(tracking=True)

    def button_cancel(self):
        res = super().button_cancel()
        for move in self:
            move.message_post(body=_('Journal Entry cancelled.'))
        return res
