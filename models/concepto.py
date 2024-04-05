# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class Concepto(models.Model):

    _inherit = ['mail.thread']
    _name = 'caja.concepto'
    _description = 'Concepto'
    _order = 'name'

    active = fields.Boolean(
        string='Activo',
        default=True,
        tracking=True)
    name = fields.Char(
        string='Nombre',
        required=True,
        tracking=True)
    notas = fields.Text()
    color = fields.Integer()
    movimiento_ids = fields.One2many('caja.movimiento', 'concepto_id',
        string='Movimientos')
    total_movimientos = fields.Integer(
        compute='_compute_total_movimientos_concepto',
        string='Total movimientos',
        store=True)

    _sql_constraints = [
        ('name_key', 'UNIQUE (name)',  'El nombre ya se encuentra registrado')
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name'):
                vals['name'] = ' '.join(vals['name'].split()).upper()
        return super(Concepto, self).create(vals_list)

    def write(self, vals):
        if vals.get('name'):
            vals['name'] = ' '.join(vals['name'].split()).upper()
        return super(Concepto, self).write(vals)
    
    def copy(self):
        raise UserError('No está permitido duplicar registros en este contexto.')
    
    @api.depends('movimiento_ids.active', 'movimiento_ids.concepto_id')
    def _compute_total_movimientos_concepto(self):
        for foo in self:
            foo.total_movimientos = len(foo.movimiento_ids)
