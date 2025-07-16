# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
import logging

_logger = logging.getLogger(__name__)


class StockWarehouse(models.Model):
    """Extensión de almacén para gestión de restricciones de usuario"""
    _inherit = "stock.warehouse"

    almus_user_ids = fields.Many2many(
        comodel_name='res.users',
        relation='almus_warehouse_allowed_users_rel',
        column1='warehouse_id',
        column2='user_id',
        string='Usuarios Permitidos',
        domain=lambda self: [
            ('groups_id', 'in', self.env.ref('stock.group_stock_user').id)
        ],
        default=lambda self: self.env.user,
        help='Usuarios que pueden acceder a este almacén'
    )
    
    almus_restrict_locations = fields.Boolean(
        string='Restringir Ubicaciones del Almacén',
        help='Activa la restricción de ubicaciones específicas de este almacén '
             'para los usuarios seleccionados'
    )

    @api.constrains('almus_user_ids')
    def _check_almus_user_ids(self):
        """Valida que al menos un usuario esté asignado si la restricción está activa"""
        if self.env['ir.config_parameter'].sudo().get_param(
            'almus_warehouse_restriction.enabled'
        ):
            for warehouse in self:
                if not warehouse.almus_user_ids:
                    raise ValidationError(_(
                        'Debe asignar al menos un usuario al almacén %s '
                        'cuando la restricción está activa.'
                    ) % warehouse.name)

    @api.onchange('almus_restrict_locations', 'almus_user_ids')
    def _onchange_almus_restrict_locations(self):
        """
        Actualiza la configuración de restricción de ubicaciones
        para los usuarios seleccionados
        """
        if self._origin and self.almus_user_ids:
            for user in self.almus_user_ids:
                if user._origin:
                    if self.almus_restrict_locations:
                        # Activar restricción y agregar almacén a permitidos
                        user._origin.write({
                            'almus_restrict_locations': True,
                            'almus_allowed_warehouse_ids': [(4, self._origin.id)]
                        })
                        _logger.info(
                            'Activada restricción de ubicaciones para usuario %s en almacén %s',
                            user.name, self.name
                        )
                    else:
                        # Solo desactivar las ubicaciones restringidas
                        user._origin.write({
                            'almus_restricted_location_ids': [(5, 0, 0)]
                        })

    def action_open_almus_users_view(self):
        """Abre la vista de usuarios para gestionar restricciones de ubicación"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Gestionar Restricciones de Usuario'),
            'view_mode': 'tree,form',
            'res_model': 'res.users',
            'domain': [
                ('id', 'in', self.almus_user_ids.ids),
                ('groups_id', 'not in', [self.env.ref('base.group_system').id])
            ],
            'context': {
                'default_almus_allowed_warehouse_ids': [(6, 0, [self.id])]
            }
        }