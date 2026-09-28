# -*- coding: utf-8 -*-
from odoo import api, models

from ..models.account_move import _analytic_names, _analytic_str

_NON_ACCOUNTING_TYPES = ('line_section', 'line_subsection', 'line_note')


class ReportSbsJournalEntryReportReport_Journal_Entries(models.AbstractModel):
    _name = 'report.sbs_journal_entry_report.report_journal_entries'
    _description = 'Journal Entry Landscape Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        lines = docs.line_ids
        # Fetch everything the template reads in a handful of queries, whatever
        # the number of entries printed from the list view.
        lines.fetch([
            'move_id', 'account_id', 'name', 'debit', 'credit', 'amount_currency',
            'currency_id', 'company_currency_id', 'partner_id', 'tax_ids',
            'analytic_distribution', 'display_type',
        ])
        lines.account_id.fetch(['code', 'name'])
        lines.partner_id.fetch(['display_name'])
        lines.tax_ids.fetch(['name'])
        names = _analytic_names(self.env, lines)

        entries = {}
        for move in docs:
            # Invoice sections and notes carry no account and no amount; the
            # 19.0 template crashed on them (account_id.code + ' - ').
            move_lines = move.line_ids.filtered(
                lambda line: line.display_type not in _NON_ACCOUNTING_TYPES
            ).sorted('id')
            rows = [{
                'line': line,
                'analytic': _analytic_str(line, names),
                'taxes': ', '.join(line.tax_ids.mapped('name')),
            } for line in move_lines]
            entries[move.id] = {
                'rows': rows,
                'total_debit': sum(move_lines.mapped('debit')),
                'total_credit': sum(move_lines.mapped('credit')),
                'show_analytic': any(row['analytic'] for row in rows),
                'show_taxes': any(row['taxes'] for row in rows),
                'show_partner': any(move_lines.mapped('partner_id')),
                # Amount in currency only says something when a line is in a
                # currency other than the company's.
                'show_currency': any(
                    line.currency_id != line.company_currency_id for line in move_lines
                ),
            }
        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': docs,
            'entries': entries,
        }
