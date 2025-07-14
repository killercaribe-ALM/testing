from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    packaging_qty_display = fields.Char(
        string='Cantidad por Empaque',
        compute='_compute_packaging_qty_display',
        store=False,
        help='Muestra la cantidad de productos en el empaque predeterminado'
    )
    
    @api.depends('packaging_ids', 'packaging_ids.qty', 'packaging_ids.sales')
    def _compute_packaging_qty_display(self):
        """Calcula la cantidad por empaque para mostrar en el catálogo"""
        # Obtener configuración
        IrConfigParam = self.env['ir.config_parameter'].sudo()
        show_packaging = IrConfigParam.get_param(
            'almus_product_packaging_display.show_packaging_qty', 'True'
        ) == 'True'
        
        if not show_packaging:
            self.packaging_qty_display = False
            return
            
        display_format = IrConfigParam.get_param(
            'almus_product_packaging_display.display_format', 'units'
        )
        
        for product in self:
            # Buscar el empaque predeterminado para ventas
            packaging = product.packaging_ids.filtered(
                lambda p: p.sales and p.qty > 0
            ).sorted('qty')
            
            if packaging:
                # Tomar el primer empaque disponible para ventas
                qty = int(packaging[0].qty) if packaging[0].qty == int(packaging[0].qty) else packaging[0].qty
                
                # Aplicar formato según configuración
                if display_format == 'units':
                    product.packaging_qty_display = f"{qty} unidades"
                elif display_format == 'pack':
                    product.packaging_qty_display = f"Empaque: {qty}"
                else:  # custom
                    product.packaging_qty_display = f"Cantidad por empaque: {qty}"
            else:
                product.packaging_qty_display = False
                
            _logger.debug('Cantidad por empaque calculada para %s: %s', 
                         product.display_name, product.packaging_qty_display)