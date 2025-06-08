    # -*- encoding: utf-8 -*-
{
    "name" : "Journal Entry Report (Landscape)",
    "version" : "18.0.0.1",
    'author' : 'STRIDE BUSINESS SOLUTIONS',
    'website' : 'https://www.stridebs.com',
    "category" : "Accounting",
    "description": """
        This module enhances journal entries in Odoo by:
        - Adding a landscape-format PDF report for journal entries.
        - Enabling chatter (communication and logging) on journal entry records for better tracking.
""",
    'license':  "AGPL-3",
    "depends" : ['account'],
    "data" : [
        'views/templates.xml',
        'views/report_actions.xml',
    ],
    "images": ['static/description/icon.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
}