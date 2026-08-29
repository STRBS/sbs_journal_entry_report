# -*- encoding: utf-8 -*-
{
    'name': 'Journal Entry Landscape',
    'version': '18.0.0.3',
    'category': 'Accounting',
    'summary': 'Landscape PDF for journal entries - wide entries with analytic distribution and taxes, readable on one page.',
    'description': """
            Odoo prints a journal entry as a portrait PDF, and it runs out of room
            the moment an entry carries analytic distribution, several taxes, or
            more than a handful of lines.

            This module adds a LANDSCAPE PDF report for journal entries, laid out
            for entries that are wide rather than long. Analytic distribution and
            tax names are flattened inline, so a reviewer sees the whole line
            instead of a column cut off at the page edge.

            It also posts an explicit note in the chatter when an entry is
            cancelled.

            Requirements
            ------------
            * Depends on Accounting (account) only. Community and Enterprise both.
            * Third-party apps install on Odoo.sh and on-premise databases only.
              They cannot be installed on Odoo Online (SaaS).
            * Odoo 18.0. Each Odoo version is sold as a separate product here.
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
