# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class Movimiento(models.Model):

    _inherit = ['mail.thread']
    _name = 'caja.movimiento'
    _description = 'Movimiento'
    _order = 'fecha desc'

    def copy(self):
        raise UserError('No está permitido duplicar registros en este contexto.')
    
    def _get_default_moneda(self):
        return self.env.ref('caja.VED').id or False

    def _get_default_currency(self):
        return self.env.ref('base.USD').id or False

    def _get_default_uom(self):
        return self.env.ref('uom.product_uom_unit').id or False

    active = fields.Boolean(
        string='Activo',
        default=True,
        tracking=True)
    name = fields.Char(
        string='Nombre',
        compute='_compute_name_movimiento',
        store=True)
    referencia = fields.Char(tracking=True)
    notas = fields.Text(tracking=True)
    color = fields.Integer()
    cantidad = fields.Float(
        default=1,
        required=True,
        tracking=True)
    tasa = fields.Float(
        compute='_compute_monto_total_movimiento',
        string='Tasa de cambio',
        store=True)
    monto_unitario = fields.Monetary(
        string='Monto unitario',
        currency_field='moneda_id',
        required=True,
        tracking=True)
    monto_unitario_usd = fields.Monetary(
        string='Monto unitario en USD',
        compute='_compute_monto_total_movimiento',
        store=True)
    monto_impuestos = fields.Monetary(
        string='Monto impuestos',
        currency_field='moneda_id',
        compute='_compute_monto_total_movimiento',
        store=True)
    monto_impuestos_usd = fields.Monetary(
        string='Monto impuestos en USD',
        compute='_compute_monto_total_movimiento',
        store=True)
    monto_total = fields.Monetary(
        string='Monto total',
        currency_field='moneda_id',
        compute='_compute_monto_total_movimiento',
        store=True)
    monto_total_usd = fields.Monetary(
        string='Monto total en USD',
        compute='_compute_monto_total_movimiento',
        store=True)
    fecha = fields.Date(
        required=True,
        default=fields.Date.today,
        tracking=True)
    company_id = fields.Many2one('res.company',
        string='Empresa',
        default=lambda self: self.env.company,
        tracking=True)
    currency_id = fields.Many2one('res.currency',
        string='Divisa',
        default=_get_default_currency,
        required=True,
        tracking=True)
    moneda_id = fields.Many2one('res.currency',
        string='Moneda',
        default=_get_default_moneda,
        required=True,
        tracking=True)
    concepto_id = fields.Many2one('caja.concepto',
        string='Concepto',
        required=True,
        tracking=True)
    proveedor_id = fields.Many2one('caja.proveedor',
        string='Proveedor',
        required=True,
        tracking=True)
    titular_id = fields.Many2one('res.users',
        string='Titular',
        default=lambda self: self.env.uid,
        required=True,
        tracking=True)
    banco_id = fields.Many2one('caja.banco',
        string='Banco',
        required=True,
        tracking=True)
    cuenta_id = fields.Many2one('caja.cuenta',
        string='Cuenta bancaria',
        required=True,
        tracking=True)
    uom_category_id = fields.Many2one('uom.category',
        string='Magnitud',
        related='uom_id.category_id',
        store=True)
    uom_id = fields.Many2one('uom.uom',
        string='Unidad',
        default=_get_default_uom,
        required=True,
        tracking=True)
    tag_ids = fields.Many2many('caja.tag', string='Etiquetas')
    total_tags = fields.Integer(
        compute='_compute_total_tags_movimiento',
        string='Total etiquetas',
        store=True)
    impuesto_ids = fields.Many2many('caja.impuesto', string='Impuestos')
    total_impuestos = fields.Integer(
        compute='_compute_total_impuestos_movimiento',
        string='Total impuestos',
        store=True)
    tipo = fields.Selection([
        ('C', 'Crédito'),
        ('D', 'Débito')
        ], string='Tipo de operación', required=True, tracking=True)
    
    @api.depends('tipo', 'fecha', 'referencia', 'concepto_id')
    def _compute_name_movimiento(self):
        for foo in self:
            if foo.tipo and foo.fecha and foo.concepto_id:
                if foo.referencia:
                    foo.name = foo.tipo + ' / ' + str(foo.fecha) + ' / ' + foo.referencia
                else:
                    foo.name = foo.tipo + ' / ' + str(foo.fecha) + ' / ' + foo.concepto_id.name
    
    @api.depends('cantidad', 'monto_unitario', 'impuesto_ids')
    def _compute_monto_total_movimiento(self):
        for foo in self:
            if foo.cantidad > 0 and foo.monto_unitario > 0:
                Historial = self.env['caja.tasa']
                resultado = Historial.search([], limit=1)
                if resultado.tasa > 0:
                    foo.tasa = resultado.tasa
                    foo.monto_unitario_usd = foo.monto_unitario / resultado.tasa
                foo.monto_total = foo.monto_unitario * foo.cantidad
                foo.monto_total_usd = foo.monto_unitario_usd * foo.cantidad
                if len(foo.impuesto_ids) == 1:
                    foo.monto_impuestos = (foo.monto_unitario * foo.cantidad) * foo.impuesto_ids.tasa / 100
                    foo.monto_impuestos_usd = (foo.monto_unitario_usd * foo.cantidad) * foo.impuesto_ids.tasa / 100
                    if foo.monto_impuestos > 0:
                        foo.monto_total = foo.monto_total + foo.monto_impuestos
                        foo.monto_total_usd = foo.monto_total_usd + foo.monto_impuestos_usd
                elif len(foo.impuesto_ids) > 1:
                    suma = sum(foo.impuesto_ids.mapped('tasa'))
                    foo.monto_impuestos = (foo.monto_unitario * foo.cantidad) * suma / 100
                    foo.monto_impuestos_usd = (foo.monto_unitario_usd * foo.cantidad) * suma / 100
                    if foo.monto_impuestos > 0:
                        foo.monto_total = foo.monto_total + foo.monto_impuestos
                        foo.monto_total_usd = foo.monto_total_usd + foo.monto_impuestos_usd
                else:
                    foo.monto_impuestos = 0
                    foo.monto_impuestos_usd = 0
    
    @api.depends('tag_ids.active')
    def _compute_total_tags_movimiento(self):
        for foo in self:
            foo.total_tags = len(foo.tag_ids)
    
    @api.depends('impuesto_ids.active')
    def _compute_total_impuestos_movimiento(self):
        for foo in self:
            foo.total_impuestos = len(foo.impuesto_ids)