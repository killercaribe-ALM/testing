# -*- coding: utf-8 -*-
{
    'name': 'Almus Supplier Visibility',
    'summary': 'Restringe la visibilidad de proveedores solo a usuarios del departamento de compras',
    'description': """
        Este módulo permite ocultar la información de proveedores para todos los usuarios
        excepto aquellos que pertenezcan al grupo de compras.
        
        Características principales:
        - Oculta automáticamente proveedores para usuarios no autorizados
        - Permite acceso completo a usuarios del departamento de compras
        - Configuración simple mediante grupos de usuarios
        - No afecta el funcionamiento normal de compras
        - Panel informativo en Configuración → Almus Dev
    """,
    'author': 'Almus Dev',
    'website': 'https://www.almus.dev',
    'category': 'Purchases',
    'version': '18.0.1.0.0',
    'license': 'LGPL-3',
    'depends': [
        'almus_base',
        'base',
        'purchase',
    ],
    'data': [
        'security/supplier_visibility_security.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}