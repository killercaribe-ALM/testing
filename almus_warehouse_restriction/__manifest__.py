# -*- coding: utf-8 -*-
{
    'name': 'Almus Warehouse Restriction',
    'summary': """
        Restricción de almacenes y ubicaciones por usuario
    """,
    'description': """
        Este módulo permite restringir el acceso a almacenes y ubicaciones
        de stock para usuarios específicos. Los usuarios solo podrán acceder
        a los almacenes y ubicaciones autorizados.
        
        Características principales:
        - Restricción de almacenes por usuario
        - Restricción de ubicaciones por almacén
        - Configuración global para activar/desactivar restricciones
        - Gestión de permisos desde el almacén
    """,
    'license': 'LGPL-3',
    'author': 'Almus Dev',
    'website': 'https://www.almus.dev',
    'category': 'Inventory/Warehouse',
    'version': '18.0.1.0.0',
    'depends': [
        'almus_base',
        'stock',
    ],
    'data': [
        'security/almus_warehouse_restriction_groups.xml',
        'security/almus_warehouse_security.xml',
        'views/res_config_settings_views.xml',
        'views/stock_warehouse_views.xml',
        'views/res_users_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}