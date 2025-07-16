# -*- coding: utf-8 -*-
from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    """Extensión de albaranes para aplicar restricciones de almacén"""
    _inherit = 'stock.picking'

    @api.onchange('location_id', 'location_dest_id')
    def _onchange_location_warehouse_restriction(self):
        """
        Aplica dominio dinámico en las ubicaciones según las restricciones
        del usuario actual
        """
        # Verificar si la restricción está activa
        if not self.env['ir.config_parameter'].sudo().get_param(
            'almus_warehouse_restriction.enabled'
        ):
            return {}
            
        # Verificar si el usuario tiene el grupo de restricción
        if not self.env.user.almus_has_warehouse_restriction:
            return {}
            
        # Aplicar dominio basado en almacenes permitidos del usuario
        domain = {
            'location_id': [
                '|',
                ('warehouse_id', '=', False),
                ('warehouse_id.almus_user_ids', 'in', self.env.user.id)
            ],
            'location_dest_id': [
                '|', 
                ('warehouse_id', '=', False),
                ('warehouse_id.almus_user_ids', 'in', self.env.user.id)
            ]
        }
        
        _logger.debug(
            'Aplicando restricción de almacén para usuario %s en picking',
            self.env.user.name
        )
        
        return {'domain': domain}

    @api.model
    def _get_default_location_id(self):
        """
        Sobrescribe el método para considerar las restricciones de almacén
        al obtener la ubicación por defecto
        """
        location = super()._get_default_location_id()
        
        # Si hay restricciones activas, validar que el usuario tenga acceso
        if (self.env['ir.config_parameter'].sudo().get_param(
                'almus_warehouse_restriction.enabled') and
                self.env.user.almus_has_warehouse_restriction and
                location and location.warehouse_id and
                self.env.user not in location.warehouse_id.almus_user_ids):
            # Buscar una ubicación alternativa en un almacén permitido
            allowed_warehouses = self.env.user.almus_allowed_warehouse_ids
            if allowed_warehouses:
                location = allowed_warehouses[0].lot_stock_id
                _logger.info(
                    'Ubicación por defecto cambiada a %s debido a restricciones',
                    location.display_name
                )
        
        return location