# -*- coding: utf-8 -*-
from lxml import html as lxml_html

from odoo import Command
from odoo.tests import tagged
from odoo.tools.misc import format_amount

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

REPORT = 'sbs_journal_entry_report.action_report_print_je'


def _text(node):
    return ' '.join(''.join(node.itertext()).replace('\xa0', ' ').split())


@tagged('post_install', '-at_install')
class TestJournalEntryReport(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # The demo databases run in Arabic: pin wording to English.
        cls.env = cls.env(context=dict(cls.env.context, lang='en_US'))
        cls.env.user.lang = 'en_US'
        cls.company = cls.company_data['company']
        cls.currency = cls.company.currency_id
        cls.foreign = cls.setup_other_currency('EUR')

        plan_a = cls.env['account.analytic.plan'].create({'name': 'Department'})
        plan_b = cls.env['account.analytic.plan'].create({'name': 'Region'})
        cls.an_sales, cls.an_ops = cls.env['account.analytic.account'].create([
            {'name': 'Sales Dept', 'plan_id': plan_a.id},
            {'name': 'Operations', 'plan_id': plan_a.id},
        ])
        cls.an_north = cls.env['account.analytic.account'].create(
            {'name': 'North Region', 'plan_id': plan_b.id})

        cls.expense = cls.company_data['default_account_expense']
        cls.revenue = cls.company_data['default_account_revenue']
        cls.bank = cls.company_data['default_journal_bank'].default_account_id

        cls.entry = cls.env['account.move'].create({
            'move_type': 'entry',
            'date': '2026-01-15',
            'ref': 'JER-REF-001',
            'journal_id': cls.company_data['default_journal_misc'].id,
            'line_ids': [
                Command.create({
                    'name': 'Rent January',
                    'account_id': cls.expense.id,
                    'partner_id': cls.partner_a.id,
                    'debit': 1000.0,
                    # "id,id" is a line spread over two plans at once: the
                    # key the 19.0 report crashed on.
                    'analytic_distribution': {
                        f'{cls.an_sales.id},{cls.an_north.id}': 60.0,
                        str(cls.an_ops.id): 40.0,
                    },
                }),
                Command.create({
                    'name': 'Paid from bank',
                    'account_id': cls.bank.id,
                    'credit': 1000.0,
                }),
            ],
        })
        cls.entry.action_post()

    def _render(self, moves, lang='en_US'):
        report = self.env['ir.actions.report'].with_context(lang=lang)
        html, _type = report._render_qweb_html(REPORT, moves.ids)
        return lxml_html.fromstring(html)

    def _cell(self, doc, name):
        nodes = doc.xpath(f'//*[@name="{name}"]')
        self.assertTrue(nodes, f'no element named {name}')
        return _text(nodes[0])

    def _money(self, amount):
        return ' '.join(format_amount(self.env, amount, self.currency).replace('\xa0', ' ').split())

    def test_report_is_attached_to_journal_entries(self):
        report = self.env.ref(REPORT)
        self.assertEqual(report.binding_model_id.model, 'account.move')
        self.assertEqual(report.paperformat_id.orientation, 'Landscape')
        self.assertFalse(report.paperformat_id.default)

    def test_report_renders_lines_totals_and_analytic(self):
        doc = self._render(self.entry)
        text = _text(doc)
        # Header: every value printed (t-esc would print nothing on 20.0).
        self.assertIn(self.entry.name, self._cell(doc, 'number'))
        self.assertIn('JER-REF-001', self._cell(doc, 'reference'))
        self.assertIn(self.entry.journal_id.name, self._cell(doc, 'journal'))
        # Lines.
        self.assertIn('Rent January', text)
        self.assertIn('Paid from bank', text)
        self.assertIn(self.expense.code, text)
        self.assertIn(self.partner_a.name, text)
        # Analytic: combined key rendered as both names, second key as one.
        self.assertIn('Sales Dept / North Region: 60.0%', text)
        self.assertIn('Operations: 40.0%', text)
        # Totals are the column sums, formatted in company currency.
        self.assertEqual(self._cell(doc, 'total_debit'), self._money(1000.0))
        self.assertEqual(self._cell(doc, 'total_credit'), self._money(1000.0))
        # Printed-by is filled in.
        self.assertIn(self.env.user.name, self._cell(doc, 'signatures'))
        # Single currency, no tax: those columns stay out.
        self.assertFalse(doc.xpath('//*[@name="th_amount_currency"]'))
        self.assertFalse(doc.xpath('//*[@name="th_taxes"]'))
        self.assertTrue(doc.xpath('//*[@name="th_analytic"]'))
        self.assertTrue(doc.xpath('//*[@name="th_partner"]'))
        page = doc.xpath('//div[contains(@class, "o_sbs_journal_entry")]')[0]
        self.assertIn('direction: ltr', page.get('style'))

    def test_vendor_bill_totals_are_positive_sums(self):
        """19.0 printed amount_total_signed in both total cells, which is
        negative on a vendor bill and ignores the tax lines' side."""
        bill = self.init_invoice(
            'in_invoice', partner=self.partner_a, invoice_date='2026-01-20',
            amounts=[500.0], taxes=self.tax_purchase_a,
        )
        # A section line must be skipped, not crash the report.
        bill.write({'invoice_line_ids': [Command.create({
            'display_type': 'line_section', 'name': 'Section A'})]})
        bill.action_post()
        doc = self._render(bill)
        debit = sum(bill.line_ids.mapped('debit'))
        self.assertGreater(debit, 500.0)
        self.assertEqual(self._cell(doc, 'total_debit'), self._money(debit))
        self.assertEqual(self._cell(doc, 'total_credit'), self._money(debit))
        self.assertIn(self.tax_purchase_a.name, self._cell(doc, 'journal_items'))
        self.assertTrue(doc.xpath('//*[@name="th_taxes"]'))
        self.assertNotIn('Section A', _text(doc))

    def test_foreign_currency_column(self):
        move = self.env['account.move'].create({
            'move_type': 'entry',
            'date': '2026-01-15',
            'line_ids': [
                Command.create({
                    'name': 'EUR expense', 'account_id': self.expense.id,
                    'currency_id': self.foreign.id,
                    'amount_currency': 300.0, 'debit': 150.0,
                }),
                Command.create({
                    'name': 'EUR bank', 'account_id': self.bank.id,
                    'currency_id': self.foreign.id,
                    'amount_currency': -300.0, 'credit': 150.0,
                }),
            ],
        })
        doc = self._render(move)
        self.assertTrue(doc.xpath('//*[@name="th_amount_currency"]'))
        cells = [_text(td) for td in doc.xpath('//*[@name="td_amount_currency"]')]
        self.assertTrue(all(cells), cells)
        self.assertIn('(Draft)', _text(doc.xpath('//h2')[0]))

    def test_several_entries_one_page_each(self):
        moves = self.entry | self.entry.copy({'date': '2026-01-16'})
        moves[1].action_post()
        doc = self._render(moves)
        self.assertEqual(len(doc.xpath('//div[contains(@class, "o_sbs_journal_entry")]')), 2)
        self.assertEqual(len(doc.xpath('//*[@name="total_debit"]')), 2)

    def test_report_query_count_does_not_grow_per_entry(self):
        moves = self.entry
        for day in range(16, 24):
            moves |= self.entry.copy({'date': f'2026-01-{day}'})
        self.env.invalidate_all()
        report = self.env['report.sbs_journal_entry_report.report_journal_entries']
        count = self.cr.sql_log_count
        report._get_report_values(self.entry.ids)
        one = self.cr.sql_log_count - count
        self.env.invalidate_all()
        count = self.cr.sql_log_count
        values = report._get_report_values(moves.ids)
        nine = self.cr.sql_log_count - count
        self.assertEqual(len(values['entries']), 9)
        # Batched: nine entries cost at most a few more queries than one.
        self.assertLessEqual(nine, one + 3, (one, nine))

    def test_arabic_prints_rtl_with_ltr_amounts(self):
        self.env['res.lang']._activate_lang('ar_001')
        self.env['ir.module.module'].search(
            [('name', '=', 'sbs_journal_entry_report')])._update_translations(['ar_001'])
        self.env.user.lang = 'ar_001'
        doc = self._render(self.entry, lang='ar_001')
        self.assertEqual(doc.xpath('//body/@dir'), ['rtl'])
        # wkhtmltopdf ignores <body dir>: the page itself must carry the
        # CSS direction or the PDF prints left-to-right.
        page = doc.xpath('//div[contains(@class, "o_sbs_journal_entry")]')[0]
        self.assertIn('direction: rtl', page.get('style'))
        self.assertIn('o_sbs_rtl', page.get('class'))
        for name in ('total_debit', 'total_credit'):
            span = doc.xpath(f'//*[@name="{name}"]/span')[0]
            self.assertIn('o_force_ltr', span.get('class'))
        self.assertIn(self.entry.name, _text(doc))
        # The shipped ar.po reaches the printed page.
        headers = [_text(th) for th in doc.xpath('//thead//th')]
        self.assertIn('مدين', headers)
        self.assertIn('دائن', headers)

    def test_legacy_line_properties(self):
        line = self.entry.line_ids.filtered(lambda l: l.debit)
        self.assertEqual(
            set(line.analytic_distribution_str.split(', ')),
            {'Sales Dept / North Region: 60.0%', 'Operations: 40.0%'})
        self.assertEqual(line.tax_names_str, '')

    def test_cancel_posts_note(self):
        move = self.entry.copy({'date': '2026-01-17'})
        move.action_post()
        move.button_cancel()
        self.assertEqual(move.state, 'cancel')
        self.assertIn('Journal Entry cancelled.', move.message_ids.mapped('body')[0])
        doc = self._render(move)
        self.assertIn('(Cancelled)', _text(doc.xpath('//h2')[0]))
