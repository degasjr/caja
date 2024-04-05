# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from odoo import models, fields, api
from odoo.exceptions import UserError

class Tasa(models.Model):

    _name = 'caja.tasa'
    _description = 'Tasa de cambio'
    _order = 'fecha desc'

    active = fields.Boolean(
        string='Activo',
        default=True)
    name = fields.Char(
        compute='_compute_name_tasa',
        store=True,
        string='Nombre')
    fecha = fields.Date(
        string='Fecha',
        required=True,
        default=fields.Date.today)
    tasa = fields.Float(
        string='Tasa de cambio',
        required=True)
    color = fields.Integer()
    notas = fields.Text()

    def copy(self):
        raise UserError('No está permitido duplicar registros en este contexto.')
    
    @api.depends('tasa', 'fecha', 'create_uid')
    def _compute_name_tasa(self):
        for foo in self:
            if foo.create_uid:
                foo.name = foo.create_uid.name+' / '+str(foo.fecha)+' / '+str(foo.tasa)
    
    def get_content_page(self, url):
        response = requests.get(url=url, verify=False)
        if not response.status_code == requests.codes.ok:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': 'Error de comunicación con el BCV',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        else:
            return response.content
    
    def consultar_tasa_bcv(self):
        Historial = self.env['emprendimiento.tasa']
        hoy = fields.Date.today()
        resultado = Historial.search([('fecha','=',hoy)], limit=1)
        if resultado.tasa > 0:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': 'Ya fue registrada la tasa de cambio del día de hoy, consulte de nuevo mañana',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        else:
            portal = BeautifulSoup(self.get_content_page("https://www.bcv.org.ve/"), "html.parser")
            seccion = portal.find("div", "view-tipo-de-cambio-oficial-del-bcv")
            tasa = seccion.find(id="dolar").find("strong").text.strip().replace(',', '.')
            if tasa:
                data = {
                    'fecha': hoy,
                    'tasa': float(tasa)
                }
                self.env['emprendimiento.tasa'].create(data)
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': 'Ha sido registrada la tasa de cambio del día de hoy',
                        'type': 'success',
                        'sticky': False,
                    }
                }