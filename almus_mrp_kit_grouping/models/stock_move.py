from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'
    
    # Campo para identificar el kit padre al que pertenece este ingrediente
    almus_parent_kit_id = fields.Many2one(
        'product.product',
        string='Kit Padre',
        help='Producto kit del cual este ingrediente forma parte',
        index=True,
    )
    
    # Nivel en la jerarquía del BoM (0 = nivel superior, 1 = primer subnivel, etc.)
    almus_bom_level = fields.Integer(
        string='Nivel en BoM',
        default=0,
        help='Nivel de profundidad en la estructura del BoM',
    )
    
    # Campo para ordenar correctamente los ingredientes agrupados
    almus_kit_sequence = fields.Integer(
        string='Secuencia en Kit',
        default=10,
        help='Orden de aparición dentro del grupo del kit',
    )
    
    # Campo computado para mostrar el nombre completo con indentación
    almus_display_name = fields.Char(
        string='Nombre para Mostrar',
        compute='_compute_almus_display_name',
    )
    
    @api.depends('product_id', 'almus_bom_level', 'almus_parent_kit_id')
    def _compute_almus_display_name(self):
        """Calcula el nombre a mostrar con indentación según el nivel"""
        for move in self:
            if move.almus_parent_kit_id:
                # Agregar indentación visual según el nivel
                indent = "    " * move.almus_bom_level
                move.almus_display_name = f"{indent}↳ {move.product_id.display_name}"
            else:
                move.almus_display_name = move.product_id.display_name