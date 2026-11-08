# -*- coding: utf-8 -*-
from odoo import models, fields, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @property
    def analytic_distribution_str(self):
        """Analytic distribution as 'Account: 100%' text.

        A key is one account id, or several ids joined by commas when the
        line is split across analytic plans (e.g. '339,1831'); int() on such
        a key crashed the report. Accounts are read with sudo so printing is
        not stopped by analytic read rights.
        """
        if not self.analytic_distribution:
            return ''
        Analytic = self.env['account.analytic.account'].sudo()
        parts = []
        for key, percent in self.analytic_distribution.items():
            ids = [int(i) for i in str(key).split(',') if i.strip().isdigit()]
            names = ' / '.join(Analytic.browse(ids).exists().mapped('name'))
            if names:
                parts.append('%s: %s%%' % (names, ('%.2f' % percent).rstrip('0').rstrip('.')))
        return ', '.join(parts)

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
