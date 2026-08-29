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
    # Checked against odoo/addons/account/models/account_move.py on 17.0, 18.0
    # and 19.0: core already declares ref, date, state and partner_id with
    # tracking=True. This module used to re-declare ref and date with
    # tracking=True, which changed nothing at all -- removed.
    #
    # What the module actually contributes is the landscape report, the two
    # helper properties above that flatten analytic distribution and tax names
    # for it, and the explicit cancellation note below.
    _inherit = 'account.move'

    def button_cancel(self):
        res = super().button_cancel()
        for move in self:
            move.message_post(body=_('Journal Entry cancelled.'))
        return res
