from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class SaleValidationLog(models.Model):
    _name = 'sale.validation.log'
    _description = 'Registro de Validaciones de Ventas'
    _order = 'create_date desc'
    _rec_name = 'sale_order_id'
    
    # Relación con la orden de venta
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Orden de Venta',
        required=True,
        ondelete='cascade',
        index=True
    )
    
    # Tipo de validación
    validation_type = fields.Selection([
        ('seller', 'Validación del Vendedor'),
        ('analyst', 'Validación del Analista'),
        ('collection', 'Validación de Cobranzas')
    ], string='Tipo de Validación', required=True)
    
    # Acción tomada
    action = fields.Selection([
        ('approve', 'Aprobado'),
        ('reject', 'Rechazado'),
        ('request_changes', 'Cambios Solicitados')
    ], string='Acción', required=True)
    
    # Usuario que validó
    user_id = fields.Many2one(
        'res.users',
        string='Validador',
        required=True,
        default=lambda self: self.env.user
    )
    
    # Fecha y hora de validación
    validation_date = fields.Datetime(
        string='Fecha de Validación',
        default=fields.Datetime.now,
        required=True
    )
    
    # Comentarios
    comments = fields.Text(
        string='Comentarios',
        help='Observaciones o razones de la decisión'
    )
    
    # Estado de la orden al momento de validar
    order_state = fields.Char(
        string='Estado de la Orden',
        help='Estado de la orden al momento de la validación'
    )
    
    # Monto de la orden al momento de validar
    order_amount = fields.Float(
        string='Monto Total',
        help='Monto total de la orden al momento de la validación'
    )
    
    @api.model_create_multi
    def create(self, vals_list):
        """Registrar información adicional al crear el log"""
        for vals in vals_list:
            if 'sale_order_id' in vals:
                order = self.env['sale.order'].browse(vals['sale_order_id'])
                vals['order_state'] = order.state
                vals['order_amount'] = order.amount_total
                
        records = super().create(vals_list)
        
        # Log en el sistema
        for record in records:
            _logger.info(
                'Validación %s: Orden %s - Acción: %s por usuario %s',
                record.validation_type,
                record.sale_order_id.name,
                record.action,
                record.user_id.name
            )
            
        return records
    
    def name_get(self):
        """Nombre descriptivo para el registro"""
        result = []
        for record in self:
            name = f"{record.sale_order_id.name} - {dict(self._fields['validation_type'].selection).get(record.validation_type)}"
            result.append((record.id, name))
        return result