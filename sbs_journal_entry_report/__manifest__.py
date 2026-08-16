# -*- encoding: utf-8 -*-
{
    'name': 'Journal Entry Report (Landscape)',
    'version': '19.0.0.2',
    'category': 'Accounting',
    'summary': 'Print Journal Entries in Landscape PDF Format with Chatter Support',
    'description': """
            Journal entries print as a portrait PDF that runs out of room the moment an
            entry has analytic distribution, several taxes, or more than a handful of lines.

            This module adds a landscape-oriented PDF report for journal entries, laid out
            for entries that are wide rather than long: analytic distribution and tax names
            are rendered inline, so a reviewer sees the whole line without scrolling a page
            sideways.

            It also turns on change tracking for the Reference and Date fields, and logs a
            note when an entry is cancelled, so those changes appear in the entry's chatter.

            Runs on Odoo Community and Enterprise.
        """,
    'author': 'STRIDE Business Solutions',
    'website': 'https://www.stridebs.com',
    'support': 'support@stridebs.com',
    'images': ['images/thumbnail.png'],
    'license': 'LGPL-3',
    # currency_rate_live is Enterprise-only and was never referenced by this
    # module; it came across from the client project this was extracted from
    # and was the only thing forcing Enterprise. account already depends on mail.
    'depends': ['account'],
    'data': [
        'views/templates.xml',
        'views/report_actions.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
