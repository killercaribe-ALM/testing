from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    almus_show_packaging_qty = fields.Boolean(
        string='Mostrar Cantidad por Empaque',
        config_parameter='almus_product_packaging_display.show_packaging_qty',
        default=True,
        help='Muestra la cantidad de productos por empaque en el catálogo de ventas'
    )
    
    almus_packaging_display_format = fields.Selection([
        ('units', 'X unidades'),
        ('pack', 'Empaque: X'),
        ('custom', 'Cantidad por empaque: X')
    ], string='Formato de Visualización',
        config_parameter='almus_product_packaging_display.display_format',
        default='units',
        help='Define cómo se muestra la información de empaque'
    )