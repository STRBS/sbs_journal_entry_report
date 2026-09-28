# sbs_journal_entry_report
Odoo module to print well-formatted journal entries in landscape layout (this branch: Odoo 20.0)

## Changelog

### 20.0.1.0.0 (2026-09-28)
- Ported to Odoo 20.0: `report_file` removed from the report action, every `t-esc` replaced by `t-out` (20.0 silently prints nothing for `t-esc` in reports).
- Totals are now the sums of the debit and credit columns. Up to 19.0 both cells showed the entry's signed total, which is negative on vendor bills and refunds.
- Debit, credit and amount-in-currency are formatted with their currency; the amount-in-currency column appears only when a line is in a foreign currency.
- Fixed a crash on lines spread over several analytic plans (combined distribution keys such as `12,34`); invoice section and note lines are skipped instead of crashing the report.
- Report data is prepared by `report.sbs_journal_entry_report.report_journal_entries` in a fixed number of queries, however many entries are printed.
- One page per entry with its own company header; draft and cancelled entries are marked in the title; the internal note prints as formatted text instead of raw HTML.
- Arabic translation (`i18n/ar.po`) and a right-to-left layout for right-to-left languages (wkhtmltopdf ignores the `dir` attribute Odoo sets on the page body, so the report sets the CSS direction itself); amounts stay left-to-right.
- The landscape paper format is no longer flagged as a default paper format.
- LICENSE now carries the LGPL-3 text the manifest declares (it was the GPL-3 text).
- Tests: report rendering, totals, analytic, taxes, currency, multi-entry, query count, Arabic/RTL, cancel note.
