from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    almus_mrp_kit_grouping_enabled = fields.Boolean(
        string='Agrupar por Kits por Defecto',
        config_parameter='almus_mrp_kit_grouping.enable_by_default',
        default=True,
        help='Habilita la agrupación de ingredientes por kit en las nuevas órdenes de fabricación',
    )
    
    almus_mrp_kit_show_indent = fields.Boolean(
        string='Mostrar Indentación Visual',
        config_parameter='almus_mrp_kit_grouping.show_indent',
        default=True,
        help='Muestra indentación visual (↳) para identificar componentes de kits',
    )
    
    almus_mrp_kit_collapse_by_default = fields.Boolean(
        string='Colapsar Kits por Defecto',
        config_parameter='almus_mrp_kit_grouping.collapse_by_default',
        default=False,
        help='Los kits aparecerán colapsados por defecto en las órdenes de fabricación',
    )