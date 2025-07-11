{
    'name': 'Almus Triple Validación de Ventas',
    'summary': 'Sistema de triple validación para órdenes de venta con aprobación secuencial',
    'description': """
        Este módulo implementa un sistema de control de calidad para órdenes de venta
        mediante tres niveles de validación secuencial:
        
        1. Validación del Vendedor - Revisa información comercial
        2. Validación del Analista - Evalúa disponibilidad y rentabilidad
        3. Validación de Cobranzas - Verifica riesgo crediticio
        
        Características:
        - Flujo de aprobación configurable
        - Historial completo de validaciones
        - Notificaciones automáticas
        - Control por montos mínimos
        - Permisos granulares por rol
    """,
    'author': 'Almus Dev',
    'website': 'https://www.almus.dev',
    'category': 'Sales',
    'version': '18.0.1.0.0',
    'license': 'LGPL-3',
    'depends': [
        'almus_base',
        'sale',
        'sale_management',
    ],
    'data': [
        # Seguridad
        'security/almus_sale_triple_validation_security.xml',
        'security/ir.model.access.csv',
        
        # Datos
        'data/sale_order_states.xml',
        
        # Vistas
        'views/res_config_settings_views.xml',
        'views/sale_order_views.xml',
        'views/sale_validation_log_views.xml',
        'wizard/sale_validation_reject_wizard_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}