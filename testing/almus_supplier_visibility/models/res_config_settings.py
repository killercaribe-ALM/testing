# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # Campo para mostrar usuarios con acceso a proveedores
    almus_supplier_visibility_users = fields.Many2many(
        'res.users',
        string='Usuarios con Acceso a Proveedores',
        compute='_compute_supplier_visibility_users',
        help='Usuarios que actualmente pueden ver información de proveedores'
    )
    
    # Estadísticas informativas
    almus_supplier_count = fields.Integer(
        string='Total de Proveedores',
        compute='_compute_supplier_stats',
        help='Número total de proveedores en el sistema'
    )
    
    almus_hidden_supplier_count = fields.Integer(
        string='Proveedores Ocultos',
        compute='_compute_supplier_stats',
        help='Número de proveedores ocultos para usuarios sin permisos'
    )
    
    @api.depends('almus_supplier_visibility_users')
    def _compute_supplier_visibility_users(self):
        for record in self:
            supplier_group = self.env.ref('almus_supplier_visibility.group_supplier_visibility', raise_if_not_found=False)
            if supplier_group:
                record.almus_supplier_visibility_users = supplier_group.users
            else:
                record.almus_supplier_visibility_users = False
    
    @api.depends('almus_supplier_count')
    def _compute_supplier_stats(self):
        for record in self:
            # Contar todos los proveedores sin aplicar reglas de registro
            all_suppliers = self.env['res.partner'].sudo().search_count([
                ('is_company', '=', True),
                ('supplier_rank', '>', 0)
            ])
            record.almus_supplier_count = all_suppliers
            
            # Calcular cuántos están ocultos (todos si el usuario no tiene permisos)
            user_has_access = self.env.user.has_group('almus_supplier_visibility.group_supplier_visibility')
            record.almus_hidden_supplier_count = 0 if user_has_access else all_suppliers
    
    def action_view_supplier_group_users(self):
        """Acción para ver usuarios con acceso a proveedores"""
        supplier_group = self.env.ref('almus_supplier_visibility.group_supplier_visibility')
        return {
            'name': 'Usuarios con Acceso a Proveedores',
            'type': 'ir.actions.act_window',
            'res_model': 'res.users',
            'view_mode': 'tree,form',
            'domain': [('groups_id', 'in', supplier_group.id)],
            'context': {'create': False}
        }
