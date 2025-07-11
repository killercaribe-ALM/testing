# -*- coding: utf-8 -*-

import re
import logging
from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    l10n_ve_document_type = fields.Selection([
        ('V', 'V - Venezolano'),
        ('E', 'E - Extranjero'),
        ('J', 'J - Jurídico'),
        ('G', 'G - Gobierno'),
        ('P', 'P - Pasaporte'),
        ('C', 'C - Comuna/Consejo Comunal'),
    ], string='Tipo de Documento', help='Tipo de documento fiscal venezolano según SENIAT')

    @api.depends('l10n_ve_document_type', 'vat')
    def _compute_l10n_ve_full_rif(self):
        """Calcula el RIF completo combinando tipo y número"""
        for partner in self:
            if partner.l10n_ve_document_type and partner.vat:
                # Limpiar el VAT de cualquier letra o guión existente
                clean_vat = re.sub(r'[^0-9]', '', partner.vat)
                partner.l10n_ve_full_rif = f"{partner.l10n_ve_document_type}-{clean_vat}"
            else:
                partner.l10n_ve_full_rif = False

    l10n_ve_full_rif = fields.Char(
        string='RIF Completo',
        compute='_compute_l10n_ve_full_rif',
        store=True,
        help='RIF completo en formato venezolano (Tipo-Número)'
    )

    @api.depends('is_company')
    def _compute_l10n_ve_show_document_fields(self):
        """Determina si mostrar los campos de documento venezolano"""
        # Verificar si existen los campos supplier_rank y customer_rank
        has_purchase = 'supplier_rank' in self._fields
        has_sale = 'customer_rank' in self._fields
        
        for partner in self:
            # Por defecto, mostrar para empresas
            show = partner.is_company
            
            # Si no es empresa, verificar si es cliente o proveedor
            if not show and (has_purchase or has_sale):
                if has_purchase and partner.supplier_rank > 0:
                    show = True
                elif has_sale and partner.customer_rank > 0:
                    show = True
            
            partner.l10n_ve_show_document_fields = show

    l10n_ve_show_document_fields = fields.Boolean(
        string='Mostrar campos de documento venezolano',
        compute='_compute_l10n_ve_show_document_fields',
        help='Campo técnico para controlar la visibilidad de campos venezolanos'
    )

    @api.constrains('vat', 'l10n_ve_document_type')
    def _check_ve_document_format(self):
        """Validar formato del documento venezolano"""
        for partner in self:
            if partner.l10n_ve_document_type and partner.vat:
                # Verificar que el módulo esté habilitado
                if not self.env['ir.config_parameter'].sudo().get_param(
                    'l10n_ve_almus_document_type.enable_validation', False
                ):
                    continue
                    
                # Limpiar el VAT de letras y caracteres especiales
                clean_vat = re.sub(r'[^0-9]', '', partner.vat)
                
                # Validar que solo contenga números después de limpiar
                if not clean_vat.isdigit():
                    raise ValidationError(
                        f"El número de documento debe contener solo dígitos. "
                        f"Valor actual: {partner.vat}"
                    )
                
                # Validar longitud según tipo de documento
                min_length = 7
                max_length = 9
                
                if len(clean_vat) < min_length or len(clean_vat) > max_length:
                    raise ValidationError(
                        f"El número de documento debe tener entre {min_length} y {max_length} dígitos. "
                        f"Longitud actual: {len(clean_vat)}"
                    )

    @api.onchange('l10n_ve_document_type')
    def _onchange_l10n_ve_document_type(self):
        """Verificar si el tipo de documento es obligatorio según configuración"""
        if self.vat and not self.l10n_ve_document_type:
            if self.env['ir.config_parameter'].sudo().get_param(
                'l10n_ve_almus_document_type.require_document_type', False
            ):
                return {
                    'warning': {
                        'title': 'Tipo de documento requerido',
                        'message': 'Se requiere seleccionar un tipo de documento cuando se ingresa un número fiscal.'
                    }
                }

    @api.model_create_multi
    def create(self, vals_list):
        """Override create para logging"""
        partners = super().create(vals_list)
        for partner in partners:
            if partner.l10n_ve_document_type:
                _logger.info(
                    'Contacto creado con tipo de documento venezolano: %s - %s por usuario %s',
                    partner.l10n_ve_document_type,
                    partner.name,
                    self.env.user.name
                )
        return partners

    def write(self, vals):
        """Override write para logging"""
        if 'l10n_ve_document_type' in vals or 'vat' in vals:
            _logger.info(
                'Actualizando documento venezolano para contacto %s por usuario %s',
                self.name,
                self.env.user.name
            )
        return super().write(vals)