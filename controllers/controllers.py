# -*- coding: utf-8 -*-
# from odoo import http


# class Caja(http.Controller):
#     @http.route('/caja/caja', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/caja/caja/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('caja.listing', {
#             'root': '/caja/caja',
#             'objects': http.request.env['caja.caja'].search([]),
#         })

#     @http.route('/caja/caja/objects/<model("caja.caja"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('caja.object', {
#             'object': obj
#         })
