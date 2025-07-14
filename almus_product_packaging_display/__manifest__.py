{
    "name": "Almus Product Packaging Display",
    "summary": """
        Muestra la cantidad por empaque en el catálogo de ventas
    """,
    "description": """
        Este módulo agrega la visualización de la cantidad de productos por empaque
        en el catálogo de productos de la aplicación de ventas de Odoo 18.
        
        Características:
        - Muestra "Cantidad por empaque: X unidades" en el catálogo
        - Mejora la experiencia del usuario al proporcionar información completa
        - Reduce errores en pedidos por falta de información
    """,
    "license": "LGPL-3",
    "author": "Almus Dev",
    "website": "https://www.almus.dev",
    "category": "Sales",
    "version": "18.0.1.0.0",
    "depends": ["almus_base", "sale", "product", "stock"],
    "installable": True,
    "auto_install": False,
    "application": True,
    "data": [
        "security/ir.model.access.csv",
        "views/product_views.xml",
        "views/sale_views.xml",
        "views/res_config_settings_views.xml",
        "views/menu_views.xml",
    ],
}