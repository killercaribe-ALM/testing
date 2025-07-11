# -*- coding: utf-8 -*-
{
    'name': 'Almus Tipos de Documento Venezuela',
    'summary': 'Tipos de documento fiscal venezolano para contactos',
    'description': '''
        Agrega un campo de selección para especificar el tipo de documento fiscal 
        venezolano (V, E, J, G, P, C) en el formulario de contactos, complementando 
        el campo nativo de identificación fiscal de Odoo.
        
        Características:
        - Campo de selección con tipos oficiales del SENIAT
        - Integración nativa con el formulario de contactos
        - Validación de formato RIF venezolano
        - Configuración desde panel Almus
    ''',
    'author': 'Almus Dev',
    'website': 'https://www.almus.dev',
    'category': 'Localization',
    'version': '18.0.1.0.0',
    'license': 'LGPL-3',
    'depends': [
        'almus_base',
        'base',
        'contacts',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}