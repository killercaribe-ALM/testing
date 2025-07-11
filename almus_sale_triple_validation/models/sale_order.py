from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    # Estados de validación
    state = fields.Selection(
        selection_add=[
            ('pending_seller', 'Pendiente Validación Vendedor'),
            ('pending_analyst', 'Pendiente Validación Analista'),
            ('pending_collection', 'Pendiente Validación Cobranzas'),
            ('validated', 'Validada'),
        ],
        ondelete={
            'pending_seller': 'set default',
            'pending_analyst': 'set default',
            'pending_collection': 'set default',
            'validated': 'set default',
        }
    )
    
    # Campos de tracking de validaciones
    seller_validated = fields.Boolean(
        string='Validado por Vendedor',
        default=False,
        copy=False
    )
    
    seller_validated_by = fields.Many2one(
        'res.users',
        string='Validado por (Vendedor)',
        copy=False
    )
    
    seller_validated_date = fields.Datetime(
        string='Fecha Validación Vendedor',
        copy=False
    )
    
    analyst_validated = fields.Boolean(
        string='Validado por Analista',
        default=False,
        copy=False
    )
    
    analyst_validated_by = fields.Many2one(
        'res.users',
        string='Validado por (Analista)',
        copy=False
    )
    
    analyst_validated_date = fields.Datetime(
        string='Fecha Validación Analista',
        copy=False
    )
    
    collection_validated = fields.Boolean(
        string='Validado por Cobranzas',
        default=False,
        copy=False
    )
    
    collection_validated_by = fields.Many2one(
        'res.users',
        string='Validado por (Cobranzas)',
        copy=False
    )
    
    collection_validated_date = fields.Datetime(
        string='Fecha Validación Cobranzas',
        copy=False
    )
    
    # Relación con logs de validación
    validation_log_ids = fields.One2many(
        'sale.validation.log',
        'sale_order_id',
        string='Historial de Validaciones'
    )
    
    validation_log_count = fields.Integer(
        string='Número de Validaciones',
        compute='_compute_validation_log_count'
    )
    
    # Campo para indicar si requiere validación
    requires_validation = fields.Boolean(
        string='Requiere Validación',
        compute='_compute_requires_validation',
        store=True
    )
    
    @api.depends('amount_total', 'state')
    def _compute_requires_validation(self):
        """Determina si la orden requiere validación basado en configuración"""
        enabled = self._is_validation_enabled()
        min_amount = float(self.env['ir.config_parameter'].sudo().get_param(
            'almus_sale_triple_validation.min_amount', '0'
        ))
        
        for order in self:
            order.requires_validation = (
                enabled and 
                order.amount_total >= min_amount and
                order.state not in ['done', 'cancel']
            )
    
    @api.depends('validation_log_ids')
    def _compute_validation_log_count(self):
        for order in self:
            order.validation_log_count = len(order.validation_log_ids)
    
    def _is_validation_enabled(self):
        """Verifica si la funcionalidad está activada"""
        return self.env['ir.config_parameter'].sudo().get_param(
            'almus_sale_triple_validation.enabled', 'False'
        ).lower() == 'true'
    
    def _can_skip_validation(self):
        """Verifica si se puede saltar la validación"""
        allow_skip = self.env['ir.config_parameter'].sudo().get_param(
            'almus_sale_triple_validation.allow_skip', 'False'
        ).lower() == 'true'
        
        return allow_skip and self.env.user.has_group('almus_sale_triple_validation.group_validation_manager')
    
    def action_confirm(self):
        """Override para implementar el flujo de validación"""
        for order in self:
            # Si no está activa la validación o no requiere validación, flujo normal
            if not order.requires_validation or order._can_skip_validation():
                return super(SaleOrder, order).action_confirm()
            
            # Si requiere validación, iniciar el proceso
            if order.state == 'draft':
                order.state = 'pending_seller'
                order._create_validation_notification('seller')
                
        return True
    
    def action_validate_seller(self):
        """Acción para validación del vendedor"""
        self.ensure_one()
        
        # Verificar permisos
        if not self.env.user.has_group('almus_sale_triple_validation.group_sale_validator_seller'):
            raise AccessError(_('No tiene permisos para realizar la validación del vendedor.'))
        
        # Verificar que el usuario sea el vendedor de la orden
        if self.user_id != self.env.user and not self.env.user.has_group('almus_sale_triple_validation.group_validation_manager'):
            raise UserError(_('Solo el vendedor asignado puede validar esta etapa.'))
        
        # Registrar validación
        self.seller_validated = True
        self.seller_validated_by = self.env.user
        self.seller_validated_date = fields.Datetime.now()
        
        # Crear log
        self._create_validation_log('seller', 'approve')
        
        # Avanzar al siguiente estado
        self.state = 'pending_analyst'
        self._create_validation_notification('analyst')
        
        return True
    
    def action_validate_analyst(self):
        """Acción para validación del analista"""
        self.ensure_one()
        
        # Verificar permisos
        if not self.env.user.has_group('almus_sale_triple_validation.group_sale_validator_analyst'):
            raise AccessError(_('No tiene permisos para realizar la validación del analista.'))
        
        # Registrar validación
        self.analyst_validated = True
        self.analyst_validated_by = self.env.user
        self.analyst_validated_date = fields.Datetime.now()
        
        # Crear log
        self._create_validation_log('analyst', 'approve')
        
        # Avanzar al siguiente estado
        self.state = 'pending_collection'
        self._create_validation_notification('collection')
        
        return True
    
    def action_validate_collection(self):
        """Acción para validación de cobranzas"""
        self.ensure_one()
        
        # Verificar permisos
        if not self.env.user.has_group('almus_sale_triple_validation.group_sale_validator_collection'):
            raise AccessError(_('No tiene permisos para realizar la validación de cobranzas.'))
        
        # Registrar validación
        self.collection_validated = True
        self.collection_validated_by = self.env.user
        self.collection_validated_date = fields.Datetime.now()
        
        # Crear log
        self._create_validation_log('collection', 'approve')
        
        # Marcar como validada y confirmar
        self.state = 'validated'
        
        # Ahora sí confirmar la orden
        return super(SaleOrder, self).action_confirm()
    
    def action_reject_validation(self):
        """Acción genérica para rechazar en cualquier etapa"""
        self.ensure_one()
        
        # Determinar en qué etapa estamos
        validation_type = None
        if self.state == 'pending_seller' and self.env.user.has_group('almus_sale_triple_validation.group_sale_validator_seller'):
            validation_type = 'seller'
        elif self.state == 'pending_analyst' and self.env.user.has_group('almus_sale_triple_validation.group_sale_validator_analyst'):
            validation_type = 'analyst'
        elif self.state == 'pending_collection' and self.env.user.has_group('almus_sale_triple_validation.group_sale_validator_collection'):
            validation_type = 'collection'
        else:
            raise AccessError(_('No tiene permisos para rechazar en esta etapa.'))
        
        # Abrir wizard para capturar motivo del rechazo
        return {
            'name': _('Rechazar Validación'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.validation.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_order_id': self.id,
                'default_validation_type': validation_type,
            }
        }
    
    def _create_validation_log(self, validation_type, action, comments=''):
        """Crear registro en el log de validaciones"""
        self.env['sale.validation.log'].create({
            'sale_order_id': self.id,
            'validation_type': validation_type,
            'action': action,
            'comments': comments,
        })
    
    def _create_validation_notification(self, validation_type):
        """Crear notificación para el siguiente validador"""
        if not self.env['ir.config_parameter'].sudo().get_param(
            'almus_sale_triple_validation.notifications', 'True'
        ).lower() == 'true':
            return
        
        # Aquí se puede implementar el envío de notificaciones
        # Por ahora solo logueamos
        _logger.info(
            'Notificación de validación %s pendiente para orden %s',
            validation_type,
            self.name
        )
    
    def action_view_validation_logs(self):
        """Ver historial de validaciones"""
        self.ensure_one()
        return {
            'name': _('Historial de Validaciones'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.validation.log',
            'view_mode': 'tree,form',
            'domain': [('sale_order_id', '=', self.id)],
            'context': {'default_sale_order_id': self.id}
        }