from odoo import models, fields, api
from collections import defaultdict
import logging

_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
    # Campo para habilitar/deshabilitar la agrupación por kit
    almus_group_by_kit = fields.Boolean(
        string='Agrupar por Kit',
        default=lambda self: self._get_default_group_by_kit(),
        help='Agrupa los ingredientes según el kit al que pertenecen',
    )
    
    # Movimientos agrupados por kit (computado)
    almus_grouped_move_ids = fields.Many2many(
        'stock.move',
        compute='_compute_grouped_moves',
        string='Materiales Agrupados',
    )
    
    def _get_default_group_by_kit(self):
        """Obtiene el valor por defecto desde la configuración"""
        return self.env['ir.config_parameter'].sudo().get_param(
            'almus_mrp_kit_grouping.enable_by_default', 
            default=True
        )
    
    @api.depends('move_raw_ids', 'almus_group_by_kit')
    def _compute_grouped_moves(self):
        """Organiza los movimientos agrupados por kit padre"""
        for production in self:
            if not production.almus_group_by_kit:
                production.almus_grouped_move_ids = production.move_raw_ids
            else:
                # Agrupar movimientos por kit
                grouped_moves = self._group_moves_by_kit(production.move_raw_ids)
                production.almus_grouped_move_ids = grouped_moves
    
    def _group_moves_by_kit(self, moves):
        """
        Agrupa los movimientos por kit padre manteniendo el orden jerárquico
        """
        if not moves:
            return moves
        
        # Crear diccionarios para búsqueda rápida
        moves_by_product = {move.product_id.id: move for move in moves}
        kit_groups = defaultdict(list)
        root_moves = []
        processed = set()
        
        # Clasificar movimientos
        for move in moves:
            if move.almus_parent_kit_id:
                kit_groups[move.almus_parent_kit_id.id].append(move)
            else:
                root_moves.append(move)
        
        # Construir lista ordenada
        ordered_move_ids = []
        
        def add_kit_and_components(kit_product_id, level=0):
            """Función recursiva para agregar kits y sus componentes"""
            if kit_product_id in processed:
                return
                
            # Buscar el movimiento del kit
            if kit_product_id in moves_by_product:
                kit_move = moves_by_product[kit_product_id]
                if kit_move.id not in ordered_move_ids:
                    ordered_move_ids.append(kit_move.id)
                    processed.add(kit_product_id)
            
            # Agregar componentes del kit
            if kit_product_id in kit_groups:
                components = sorted(kit_groups[kit_product_id], 
                                  key=lambda m: (m.almus_kit_sequence, m.id))
                for component in components:
                    if component.id not in ordered_move_ids:
                        ordered_move_ids.append(component.id)
                    # Si el componente es también un kit, procesar recursivamente
                    if component.product_id.id in kit_groups:
                        add_kit_and_components(component.product_id.id, level + 1)
        
        # Procesar movimientos root
        for move in sorted(root_moves, key=lambda m: (m.almus_kit_sequence, m.id)):
            if move.id not in ordered_move_ids:
                ordered_move_ids.append(move.id)
            # Si es un kit, agregar sus componentes
            if move.product_id.id in kit_groups:
                add_kit_and_components(move.product_id.id, 0)
        
        # Retornar recordset ordenado
        return moves.browse(ordered_move_ids)
    
    @api.model
    def create(self, vals):
        """Override para asignar información de kit al crear la orden"""
        production = super().create(vals)
        if production.bom_id:
            production._assign_kit_information()
        return production
    
    def _assign_kit_information(self):
        """
        Asigna la información de kit padre y nivel a los movimientos
        basándose en la estructura del BoM
        """
        self.ensure_one()
        
        if not self.bom_id:
            return
        
        try:
            # Resetear información previa
            self.move_raw_ids.write({
                'almus_parent_kit_id': False,
                'almus_bom_level': 0,
                'almus_kit_sequence': 10,
            })
            
            # Mapear la estructura del BoM a los movimientos
            def process_bom_line(bom_line, parent_product=None, level=0, sequence=10):
                """Procesa recursivamente las líneas del BoM"""
                # Buscar el movimiento correspondiente
                move = self.move_raw_ids.filtered(
                    lambda m: m.product_id == bom_line.product_id and 
                    not m.almus_parent_kit_id  # Solo procesar movimientos sin asignar
                )[:1]  # Tomar solo el primero si hay múltiples
                
                if move:
                    move.write({
                        'almus_parent_kit_id': parent_product.id if parent_product else False,
                        'almus_bom_level': level,
                        'almus_kit_sequence': sequence,
                    })
                
                # Si el producto tiene su propio BoM (es un kit), procesar sus líneas
                child_bom = self.env['mrp.bom'].search([
                    ('product_id', '=', bom_line.product_id.id),
                    ('type', '=', 'normal'),
                    ('active', '=', True)
                ], limit=1)
                
                if child_bom:
                    seq = 10
                    for child_line in child_bom.bom_line_ids:
                        process_bom_line(child_line, bom_line.product_id, level + 1, seq)
                        seq += 10
            
            # Procesar todas las líneas del BoM principal
            sequence = 10
            for line in self.bom_id.bom_line_ids:
                process_bom_line(line, None, 0, sequence)
                sequence += 10
                
        except Exception as e:
            _logger.warning(f"Error asignando información de kit: {str(e)}")
            # En caso de error, continuar sin la agrupación
    
    def action_confirm(self):
        """Override para asignar información de kit al confirmar"""
        res = super().action_confirm()
        for production in self:
            if production.bom_id and production.almus_group_by_kit:
                production._assign_kit_information()
        return res