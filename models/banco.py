# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class Banco(models.Model):

    _inherit = ['mail.thread']
    _name = 'caja.banco'
    _description = 'Banco'
    _order = 'code'

    active = fields.Boolean(
        string='Activo',
        default=True,
        tracking=True)
    name = fields.Char(
        string='Nombre',
        required=True,
        tracking=True)
    code = fields.Char(
        string='Código',
        required=True,
        copy=False,
        tracking=True)
    notas = fields.Text()
    color = fields.Integer()
    cuenta_ids = fields.One2many('caja.cuenta', 'banco_id',
        string='Cuentas')
    total_cuentas = fields.Integer(
        compute='_compute_total_cuentas_banco',
        string='Total cuentas',
        store=True)
    movimiento_ids = fields.One2many('caja.movimiento', 'banco_id',
        string='Movimientos')
    total_movimientos = fields.Integer(
        compute='_compute_total_movimientos_banco',
        string='Total movimientos',
        store=True)

    _sql_constraints = [
        ('nombre_unique', 'UNIQUE (name)',  'El nombre ya existe'),
        ('codigo_unique', 'UNIQUE (code)',  'El código ya existe')
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name'):
                vals['name'] = ' '.join(vals['name'].split()).upper()
            if vals.get('code'):
                vals['code'] = ''.join(vals['code'].split())
        return super(Banco, self).create(vals_list)

    def write(self, vals):
        if vals.get('name'):
            vals['name'] = ' '.join(vals['name'].split()).upper()
        if vals.get('code'):
            vals['code'] = ''.join(vals['code'].split())
        return super(Banco, self).write(vals)
    
    def copy(self):
        raise UserError('No está permitido duplicar registros en este contexto.')
    
    @api.constrains('code')
    def _check_codigo_banco(self):
        for foo in self:
            if foo.code.isdigit() != True:
                raise ValidationError('El código del banco debe ser numérico.')
            if len(foo.code) != 4:
                raise ValidationError('El código del banco debe tener 4 dígitos de longitud.')
    
    @api.depends('cuenta_ids.active', 'cuenta_ids.banco_id')
    def _compute_total_cuentas_banco(self):
        for foo in self:
            foo.total_cuentas = len(foo.cuenta_ids)
    
    @api.depends('movimiento_ids.active', 'movimiento_ids.banco_id')
    def _compute_total_movimientos_banco(self):
        for foo in self:
            foo.total_movimientos = len(foo.movimiento_ids)

class Cuenta(models.Model):

    _inherit = ['mail.thread']
    _name = 'caja.cuenta'
    _description = 'Cuenta bancaria'
    _order = 'name'

    def _get_default_moneda(self):
        return self.env.ref('caja.VED').id or False

    def _get_default_currency(self):
        return self.env.ref('base.USD').id or False

    def copy(self):
        raise UserError('No está permitido duplicar registros en este contexto.')

    active = fields.Boolean(
        string='Activo',
        default=True,
        tracking=True)
    name = fields.Char(
        string='Número de cuenta',
        required=True,
        tracking=True)
    tasa = fields.Float(
        compute='_compute_total_movimientos_cuenta',
        string='Tasa de cambio',
        store=True)
    saldo = fields.Monetary(
        currency_field='moneda_id',
        compute='_compute_total_movimientos_cuenta',
        store=True)
    saldo_usd = fields.Monetary(
        string='Saldo en USD',
        compute='_compute_total_movimientos_cuenta',
        store=True)
    notas = fields.Text()
    color = fields.Integer()
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
    titular_id = fields.Many2one('res.users',
        string='Titular',
        default=lambda self: self.env.uid,
        required=True,
        tracking=True)
    banco_id = fields.Many2one('caja.banco',
        string='Banco',
        required=True,
        tracking=True)
    movimiento_ids = fields.One2many('caja.movimiento', 'cuenta_id',
        string='Movimientos')
    total_movimientos = fields.Integer(
        compute='_compute_total_movimientos_cuenta',
        string='Total movimientos',
        store=True)

    _sql_constraints = [
        ('cuenta_unique', 'UNIQUE (name)',  'El número de cuenta ya existe')
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name'):
                vals['name'] = ''.join(vals['name'].split())
        return super(Cuenta, self).create(vals_list)

    def write(self, vals):
        if vals.get('name'):
            vals['name'] = ''.join(vals['name'].split())
        return super(Cuenta, self).write(vals)

    @api.constrains('name')
    def _check_cuenta_banco(self):
        for foo in self:
            if foo.name.isdigit() != True:
                raise ValidationError('El valor de cuenta bancaria debe ser numérico.')
            if len(foo.name) != 20:
                raise ValidationError('El número de cuenta bancaria debe tener 20 dígitos de longitud.')
    
    @api.depends('movimiento_ids.active', 'movimiento_ids.cuenta_id', 'movimiento_ids.monto_total')
    def _compute_total_movimientos_cuenta(self):
        for foo in self:
            foo.total_movimientos = len(foo.movimiento_ids)
            if len(foo.movimiento_ids) > 0:
                Creditos = foo.movimiento_ids.filtered(lambda r: r.tipo == 'C')
                Debitos = foo.movimiento_ids.filtered(lambda r: r.tipo == 'D')
                monto_creditos = sum(Creditos.mapped('monto_total'))
                monto_debitos = sum(Debitos.mapped('monto_total'))
                foo.saldo = monto_creditos - monto_debitos
                Historial = self.env['caja.tasa']
                resultado = Historial.search([], limit=1)
                if resultado.tasa > 0:
                    foo.tasa = resultado.tasa
                    foo.saldo_usd = foo.saldo / resultado.tasa
