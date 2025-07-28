{
    "name": "Almus Agrupación de Kits en Fabricación",
    "summary": """
        Agrupa ingredientes por kits en órdenes de fabricación
    """,
    "description": """
        Este módulo mejora la visualización de las órdenes de fabricación
        agrupando los ingredientes según el kit al que pertenecen.
        
        Características principales:
        - Agrupación visual de ingredientes por kit padre
        - Interfaz expandible/colapsable para navegación intuitiva
        - Mantiene la funcionalidad original de las órdenes
        - Respeta la estructura jerárquica de las recetas multinivel
    """,
    "license": "LGPL-3",
    "author": "Almus Dev",
    "website": "https://www.almus.dev",
    "category": "Manufacturing",
    "version": "18.0.1.0.0",
    "depends": ["almus_base", "mrp", "stock"],
    "installable": True,
    "auto_install": False,
    "application": True,
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_production_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "almus_mrp_kit_grouping/static/src/js/mrp_kit_grouping.js",
            "almus_mrp_kit_grouping/static/src/xml/mrp_kit_grouping.xml",
        ],
    },
}