# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    l10n_ve_enable_document_validation = fields.Boolean(
        string='Validar formato de documento venezolano',
        config_parameter='l10n_ve_almus_document_type.enable_validation',
        help='Habilita la validación automática del formato de documentos fiscales venezolanos'
    )
    
    l10n_ve_require_document_type = fields.Boolean(
        string='Tipo de documento obligatorio',
        config_parameter='l10n_ve_almus_document_type.require_document_type',
        help='Hace obligatorio seleccionar el tipo de documento cuando se ingresa un número fiscal'
    )