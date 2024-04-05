# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from random import randint

class Impuesto(models.Model):

    _inherit = ['mail.thread']
    _name = 'caja.impuesto'
    _description = 'Impuesto'
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
    color = fields.Integer(default=lambda self: randint(1, 11))
    tasa = fields.Float(
        required=True,
        tracking=True)
    movimiento_ids = fields.Many2many('caja.movimiento', string='Movimientos')
    total_movimientos = fields.Integer(
        compute='_compute_total_movimientos_impuesto',
        string='Total movimientos',
        store=True)

    _sql_constraints = [
        ('name_unique', 'UNIQUE (name)',  'El nombre ya se encuentra registrado'),
        ('check_tasa', 'CHECK (tasa > 0)',  'La tasa debe ser mayor que cero')
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name'):
                vals['name'] = ' '.join(vals['name'].split()).upper()
        return super(Impuesto, self).create(vals_list)

    def write(self, vals):
        if vals.get('name'):
            vals['name'] = ' '.join(vals['name'].split()).upper()
        return super(Impuesto, self).write(vals)
    
    def copy(self):
        raise UserError('No está permitido duplicar registros en este contexto.')

    @api.depends('movimiento_ids.active')
    def _compute_total_movimientos_impuesto(self):
        for foo in self:
            foo.total_movimientos = len(foo.movimiento_ids)