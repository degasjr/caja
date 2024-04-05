# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class Proveedor(models.Model):

    _inherit = ['mail.thread']
    _name = 'caja.proveedor'
    _description = 'Proveedor'
    _order = 'name'

    active = fields.Boolean(
        string='Activo',
        default=True,
        tracking=True)
    name = fields.Char(
        string='Nombre',
        copy=False,
        required=True,
        tracking=True)
    rif = fields.Char(
        string='RIF',
        copy=False,
        tracking=True)
    telefono = fields.Char(
        string='Teléfono',
        tracking=True)
    notas = fields.Text()
    direccion = fields.Text(
        string='Dirección',
        tracking=True)
    color = fields.Integer()
    movimiento_ids = fields.One2many('caja.movimiento', 'proveedor_id',
        string='Movimientos')
    total_movimientos = fields.Integer(
        compute='_compute_total_movimientos_proveedor',
        string='Total movimientos',
        store=True)

    _sql_constraints = [
        ('nombre_unique', 'UNIQUE (name)',  'El proveedor ya existe'),
        ('rif_unique', 'UNIQUE (rif)',  'El RIF ya existe')
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name'):
                vals['name'] = ' '.join(vals['name'].split()).upper()
            if vals.get('rif'):
                vals['rif'] = ''.join(vals['rif'].split()).upper()
        return super(Proveedor, self).create(vals_list)

    def write(self, vals):
        if vals.get('name'):
            vals['name'] = ' '.join(vals['name'].split()).upper()
        if vals.get('rif'):
            vals['rif'] = ''.join(vals['rif'].split()).upper()
        return super(Proveedor, self).write(vals)
    
    def copy(self):
        raise UserError('No está permitido duplicar registros en este contexto.')
    
    @api.depends('movimiento_ids.active', 'movimiento_ids.proveedor_id')
    def _compute_total_movimientos_proveedor(self):
        for foo in self:
            foo.total_movimientos = len(foo.movimiento_ids)