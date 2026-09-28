# -*- coding: utf-8 -*-
from odoo import models


def _analytic_names(env, lines):
    """Return {analytic account id: name} for every account used on ``lines``.

    One read for all lines of all printed entries instead of one per
    distribution key. Keys may be combined ("12,34") when a line is spread
    over several analytic plans; the 19.0 code cast them with int() and
    crashed on those.
    """
    ids = {
        int(account_id)
        for line in lines
        for key in (line.analytic_distribution or {})
        for account_id in str(key).split(',')
        if account_id.strip()
    }
    accounts = env['account.analytic.account'].browse(ids).exists()
    return {account.id: account.display_name for account in accounts}


def _analytic_str(line, names):
    parts = []
    for key, percentage in (line.analytic_distribution or {}).items():
        label = ' / '.join(
            names[int(account_id)]
            for account_id in str(key).split(',')
            if account_id.strip() and int(account_id) in names
        )
        if label:
            parts.append('%s: %s%%' % (label, round(percentage, 2)))
    return ', '.join(parts)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # Kept for backward compatibility with 17.0-19.0, where the report template
    # read these properties. The 20.0 report prepares the same strings in bulk
    # (see report/journal_entry_report.py).
    @property
    def analytic_distribution_str(self):
        return _analytic_str(self, _analytic_names(self.env, self))

    @property
    def tax_names_str(self):
        return ', '.join(self.tax_ids.mapped('name'))


class AccountMove(models.Model):
    # Core already declares ref, date, state and partner_id with tracking=True.
    # What the module contributes is the landscape report and the explicit
    # cancellation note below.
    _inherit = 'account.move'

    def button_cancel(self):
        res = super().button_cancel()
        for move in self:
            move.message_post(body=self.env._('Journal Entry cancelled.'))
        return res
