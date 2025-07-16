# -*- coding: utf-8 -*-
from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    """Configuración para restricción de almacenes por usuario"""
    _inherit = 'res.config.settings'

    almus_warehouse_restriction_enabled = fields.Boolean(
        string="Activar Restricción de Almacenes",
        config_parameter='almus_warehouse_restriction.enabled',
        help="Activa la restricción de almacenes para usuarios específicos"
    )
    
    almus_warehouse_restriction_group = fields.Boolean(
        string="Usar grupo de restricción",
        implied_group='almus_warehouse_restriction.group_warehouse_restriction_user',
        help="Activa el grupo de seguridad para restricción de almacenes"
    )

    @api.onchange('almus_warehouse_restriction_enabled')
    def _onchange_almus_warehouse_restriction_enabled(self):
        """
        Cuando se activa la restricción, asigna el usuario actual
        a todos los almacenes existentes por defecto
        """
        if self.almus_warehouse_restriction_enabled:
            _logger.info('Activando restricción de almacenes para usuario %s', 
                        self.env.user.name)
            warehouses = self.env['stock.warehouse'].search([])
            for warehouse in warehouses:
                if not warehouse.almus_user_ids:
                    warehouse.almus_user_ids = [(6, 0, [self.env.user.id])]
        else:
            _logger.info('Desactivando restricción de almacenes')
            # Mantener los usuarios asignados pero desactivar la funcionalidad
            # No limpiamos los usuarios para no perder la configuración