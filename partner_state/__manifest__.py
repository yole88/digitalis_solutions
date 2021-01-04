# -*- coding: utf-8 -*-
{
    'name': 'Partner state',
    'version': '1.0',
    'description': ''' Partner state
    ''',
    'category': 'Partner state',
    'author': 'Admin',
    'website': '',
    'depends': [
        'base', 'project', 'account', 'web_tour'
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data_state.xml',
        'views/templates.xml',
        'views/views_state.xml',
        'views/views_partner_state.xml',
        'views/views_project.xml',
        'views/menu.xml',
    ],
    'application': True,
}
