# -*- encoding: utf-8 -*-
{
    'name': 'Journal Entry Report (Landscape)',
    'version': '18.0.0.1',
    'category': 'Accounting',
    'summary': 'Print Journal Entries in Landscape PDF Format with Chatter Support',
    'description': """
            This module enhances the accounting workflow in Odoo by providing:

            • A landscape-oriented PDF report for journal entries with a clean layout.
            • Chatter integration on journal entries for better audit trails and collaboration.

            Ideal for organizations that require formal journal entry prints or approval workflows.
        """,
    'author': 'STRIDE BUSINESS SOLUTIONS',
    'website': 'https://www.stridebs.com',
    'support': 'support@stridebs.com',
    'images': ['images/thumbnail.png'],
    'license': 'LGPL-3',
    'depends': ['account', 'mail', 'currency_rate_live'],
    'data': [
        'views/templates.xml',
        'views/report_actions.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
