from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # Campo para activar/desactivar la funcionalidad
    almus_partner_confidential_enabled = fields.Boolean(
        string='Activar Información Confidencial de Contactos',
        config_parameter='almus_partner_confidential.enabled',
        default=True,
        help='Activa la pestaña de información confidencial en los contactos'
    )
    
    # Usuarios con acceso a información confidencial
    almus_confidential_users = fields.Many2many(
        'res.users',
        string='Usuarios con Acceso',
        compute='_compute_confidential_users',
        readonly=True,
        help='Usuarios que pueden ver y editar información confidencial'
    )
    
    # Estadísticas
    almus_partners_with_confidential = fields.Integer(
        string='Contactos con Info. Confidencial',
        compute='_compute_confidential_stats',
        readonly=True
    )
    
    almus_total_confidential_users = fields.Integer(
        string='Total Usuarios con Acceso',
        compute='_compute_confidential_stats',
        readonly=True
    )
    
    @api.depends_context('uid')
    def _compute_confidential_users(self):
        """Obtener usuarios con acceso a información confidencial"""
        for record in self:
            confidential_group = self.env.ref(
                'almus_partner_confidential.group_partner_confidential_user',
                raise_if_not_found=False
            )
            if confidential_group:
                record.almus_confidential_users = confidential_group.users
            else:
                record.almus_confidential_users = False
    
    @api.depends_context('uid')
    def _compute_confidential_stats(self):
        """Calcular estadísticas de uso"""
        for record in self:
            # Contar contactos con información confidencial
            Partner = self.env['res.partner'].sudo()
            domain = [
                '|', '|', '|', '|', '|', '|', '|', '|', '|',
                ('almus_confidential_name', '!=', False),
                ('almus_confidential_email', '!=', False),
                ('almus_wechat_id', '!=', False),
                ('almus_whatsapp_number', '!=', False),
                ('almus_contact_person', '!=', False),
                ('almus_payment_terms_notes', '!=', False),
                ('almus_price_conditions', '!=', False),
                ('almus_bank_info', '!=', False),
                ('almus_internal_notes', '!=', False),
                ('almus_credit_info', '!=', False),
            ]
            record.almus_partners_with_confidential = Partner.search_count(domain)
            
            # Contar usuarios con acceso
            confidential_group = self.env.ref(
                'almus_partner_confidential.group_partner_confidential_user',
                raise_if_not_found=False
            )
            record.almus_total_confidential_users = len(confidential_group.users) if confidential_group else 0
    
    def action_view_confidential_users(self):
        """Ver usuarios con acceso a información confidencial"""
        confidential_group = self.env.ref('almus_partner_confidential.group_partner_confidential_user')
        
        return {
            'name': 'Usuarios con Acceso a Información Confidencial',
            'type': 'ir.actions.act_window',
            'res_model': 'res.users',
            'view_mode': 'list,form',
            'domain': [('groups_id', 'in', [confidential_group.id])],
            'context': {
                'create': False,
                'edit': False,
            },
            'target': 'current',
        }
    
    def action_view_confidential_partners(self):
        """Ver contactos con información confidencial"""
        domain = [
            '|', '|', '|', '|', '|', '|', '|', '|', '|',
            ('almus_confidential_name', '!=', False),
            ('almus_confidential_email', '!=', False),
            ('almus_wechat_id', '!=', False),
            ('almus_whatsapp_number', '!=', False),
            ('almus_contact_person', '!=', False),
            ('almus_payment_terms_notes', '!=', False),
            ('almus_price_conditions', '!=', False),
            ('almus_bank_info', '!=', False),
            ('almus_internal_notes', '!=', False),
            ('almus_credit_info', '!=', False),
        ]
        
        return {
            'name': 'Contactos con Información Confidencial',
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'list,form',
            'domain': domain,
            'context': {
                'create': False,
            },
            'target': 'current',
        }