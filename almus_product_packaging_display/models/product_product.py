from odoo import models, api
from odoo.tools import str2bool
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    def get_packaging_display_info(self):
        """
        Método para obtener información de empaque sin usar campos computados.
        Optimizado para uso en vistas.
        """
        # Obtener configuración una sola vez
        IrConfigParam = self.env['ir.config_parameter']
        show_packaging = str2bool(IrConfigParam.get_param(
            'almus_product_packaging_display.show_packaging_qty', 'True'
        ))
        
        if not show_packaging:
            return False
            
        display_format = IrConfigParam.get_param(
            'almus_product_packaging_display.display_format', 'units'
        )
        
        # Buscar empaque predeterminado para ventas
        packaging = self.packaging_ids.filtered(
            lambda p: p.sales and p.qty > 0
        )
        
        if not packaging:
            return False
            
        # Tomar el empaque con menor cantidad (más común)
        primary_packaging = packaging.sorted('qty')[0]
        qty = primary_packaging.qty
        
        # Formatear según configuración  
        if display_format == 'units':
            return f"{int(qty) if qty == int(qty) else qty} unidades"
        elif display_format == 'pack':
            return f"Empaque: {int(qty) if qty == int(qty) else qty}"
        else:  # custom
            return f"Cantidad por empaque: {int(qty) if qty == int(qty) else qty}"
    
    @api.model
    def get_packaging_info_for_products(self, product_ids):
        """
        Método batch para obtener información de empaque de múltiples productos.
        Útil para vistas que muestran muchos productos.
        """
        if not product_ids:
            return {}
            
        # Verificar configuración
        IrConfigParam = self.env['ir.config_parameter']
        show_packaging = str2bool(IrConfigParam.get_param(
            'almus_product_packaging_display.show_packaging_qty', 'True'
        ))
        
        if not show_packaging:
            return {}
            
        display_format = IrConfigParam.get_param(
            'almus_product_packaging_display.display_format', 'units'
        )
        
        result = {}
        products = self.browse(product_ids)
        
        for product in products:
            packaging = product.packaging_ids.filtered(
                lambda p: p.sales and p.qty > 0
            )
            
            if packaging:
                primary_packaging = packaging.sorted('qty')[0]
                qty = primary_packaging.qty
                
                if display_format == 'units':
                    result[product.id] = f"{int(qty) if qty == int(qty) else qty} unidades"
                elif display_format == 'pack':
                    result[product.id] = f"Empaque: {int(qty) if qty == int(qty) else qty}"
                else:  # custom
                    result[product.id] = f"Cantidad por empaque: {int(qty) if qty == int(qty) else qty}"
            else:
                result[product.id] = False
                
        return result


class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    def get_packaging_display_info(self):
        """
        Método delegado al template para mantener consistencia.
        """
        return self.product_tmpl_id.get_packaging_display_info()