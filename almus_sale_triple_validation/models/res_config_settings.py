from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # Activación del sistema
    almus_sale_triple_validation_enabled = fields.Boolean(
        string='Activar Triple Validación de Ventas',
        config_parameter='almus_sale_triple_validation.enabled',
        help='Activa el sistema de triple validación para órdenes de venta'
    )
    
    # Monto mínimo para requerir validación
    almus_sale_validation_min_amount = fields.Float(
        string='Monto Mínimo para Validación',
        config_parameter='almus_sale_triple_validation.min_amount',
        default=0.0,
        help='Las órdenes menores a este monto no requieren triple validación'
    )
    
    # Permitir saltar validaciones
    almus_sale_allow_skip_validation = fields.Boolean(
        string='Permitir Saltar Validaciones',
        config_parameter='almus_sale_triple_validation.allow_skip',
        help='Permite a usuarios con permisos especiales saltar el proceso de validación'
    )
    
    # Notificaciones automáticas
    almus_sale_validation_notifications = fields.Boolean(
        string='Notificaciones Automáticas',
        config_parameter='almus_sale_triple_validation.notifications',
        default=True,
        help='Envía notificaciones automáticas a los validadores cuando una orden requiere su aprobación'
    )
    
    # Tiempo máximo de respuesta (en horas)
    almus_sale_validation_timeout = fields.Integer(
        string='Tiempo Máximo de Respuesta (horas)',
        config_parameter='almus_sale_triple_validation.timeout',
        default=24,
        help='Tiempo máximo en horas para que un validador responda antes de escalar'
    )
    
    @api.model
    def set_values(self):
        """Log cuando se activa/desactiva la funcionalidad"""
        was_enabled = self.env['ir.config_parameter'].sudo().get_param(
            'almus_sale_triple_validation.enabled', 'False'
        ).lower() == 'true'
        
        super().set_values()
        
        is_enabled = self.almus_sale_triple_validation_enabled
        
        if was_enabled != is_enabled:
            _logger.info(
                'Triple Validación de Ventas %s por el usuario %s',
                'activada' if is_enabled else 'desactivada',
                self.env.user.name
            )