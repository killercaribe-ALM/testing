from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # Campo para activar/desactivar la funcionalidad
    almus_partner_confidential_enabled = fields.Boolean(
        string='Activar Información Confidencial de Contactos',
        config_parameter='almus_partner_confidential.enabled',
        help='Activa la pestaña de información confidencial en los contactos'
    )
    
    @api.model
    def get_values(self):
        """Obtener valores y sincronizar el grupo técnico"""
        res = super().get_values()
        
        # Verificar si la funcionalidad está activada
        is_enabled = self.env['ir.config_parameter'].sudo().get_param(
            'almus_partner_confidential.enabled', 'False'
        ).lower() == 'true'
        
        # Sincronizar el grupo técnico
        group_enabled = self.env.ref('almus_partner_confidential.group_partner_confidential_enabled', False)
        if group_enabled:
            all_users = self.env['res.users'].sudo().search([])
            if is_enabled:
                # Asignar el grupo a todos los usuarios si no lo tienen
                users_without_group = all_users.filtered(lambda u: group_enabled not in u.groups_id)
                if users_without_group:
                    group_enabled.users = [(4, user.id) for user in users_without_group]
            else:
                # Remover el grupo de todos los usuarios
                if group_enabled.users:
                    group_enabled.users = [(5, 0, 0)]
        
        return res
    
    @api.model
    def set_values(self):
        """Sobrescribir para manejar la activación/desactivación"""
        # Obtener el valor anterior
        was_enabled = self.env['ir.config_parameter'].sudo().get_param(
            'almus_partner_confidential.enabled', 'False'
        ).lower() == 'true'
        
        # Llamar al método padre
        super().set_values()
        
        # Obtener el valor nuevo
        is_enabled = self.almus_partner_confidential_enabled
        
        # Log del cambio
        if was_enabled != is_enabled:
            _logger.info(
                'Información Confidencial de Contactos %s por el usuario %s',
                'activada' if is_enabled else 'desactivada',
                self.env.user.name
            )
            
            # Manejar el grupo técnico
            group_enabled = self.env.ref('almus_partner_confidential.group_partner_confidential_enabled', False)
            if group_enabled:
                all_users = self.env['res.users'].sudo().search([])
                if is_enabled:
                    # Asignar el grupo a todos los usuarios
                    group_enabled.users = [(6, 0, all_users.ids)]
                else:
                    # Remover el grupo de todos los usuarios
                    group_enabled.users = [(5, 0, 0)]