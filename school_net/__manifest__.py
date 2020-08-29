# -*- coding: utf-8 -*-
{
    'name': "Pravasi Rojgar",

    'summary': """
        Pravasi Rojgar CRM Configs
        """,

    'description': """
        
    """,

    'author': "SquadSoftech",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','contacts','hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        
        'data/Skills.xml',
        'data/Configuration.xml',

        'views/SchoolNet.xml',
        'views/Clients.xml',
        'views/Calls.xml',
        'views/Messages.xml',
        'views/Activities.xml',
        'views/Partner.xml',
        'views/Logs.xml',
        'views/Campaign.xml',
        'views/templates.xml',

        
        'views/CalloutList.xml',
        'views/templates.xml',

        'data/Skills.xml',
        'data/Sequences.xml',
        'data/BulkDataPush.xml',
        'data/CallDataImport.xml'

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
