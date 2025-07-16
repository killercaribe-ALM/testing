# -*- coding: utf-8 -*-
from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    """Extensión de usuarios para restricción de almacenes y ubicaciones"""
    _inherit = 'res.users'

    almus_restrict_locations = fields.Boolean(
        string="Restringir Ubicaciones",
        help="Activa la restricción de ubicaciones para este usuario"
    )
    
    almus_restricted_location_ids = fields.Many2many(
        comodel_name='stock.location',
        relation='almus_user_restricted_locations_rel',
        column1='user_id',
        column2='location_id',
        string='Ubicaciones Restringidas',
        help='Ubicaciones a las que el usuario NO puede acceder'
    )
    
    almus_allowed_warehouse_ids = fields.Many2many(
        comodel_name='stock.warehouse',
        relation='almus_user_allowed_warehouses_rel',
        column1='user_id',
        column2='warehouse_id',
        string='Almacenes Permitidos',
        help='Almacenes a los que el usuario puede acceder'
    )
    
    almus_has_warehouse_restriction = fields.Boolean(
        string="Tiene Restricción",
        compute='_compute_almus_has_warehouse_restriction',
        help="Indica si el usuario tiene restricciones de almacén activas"
    )

    @api.depends('groups_id')
    def _compute_almus_has_warehouse_restriction(self):
        """Verifica si el usuario pertenece al grupo de restricción"""
        restriction_group = self.env.ref(
            'almus_warehouse_restriction.group_warehouse_restriction_user',
            raise_if_not_found=False
        )
        for user in self:
            user.almus_has_warehouse_restriction = (
                restriction_group and restriction_group in user.groups_id
            )

    @api.model_create_multi
    def create(self, vals_list):
        """Limpia caché al crear usuarios"""
        self.env.registry.clear_cache()
        return super().create(vals_list)

    def write(self, vals):
        """Limpia caché al modificar usuarios"""
        if any(field in vals for field in [
            'almus_restrict_locations',
            'almus_restricted_location_ids',
            'almus_allowed_warehouse_ids',
            'groups_id'
        ]):
            self.env.registry.clear_cache()
            _logger.info('Actualizando restricciones de almacén para usuarios: %s',
                        ', '.join(self.mapped('name')))
        return super().write(vals)