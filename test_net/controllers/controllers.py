# -*- coding: utf-8 -*-
# from odoo import http


# class TestNet(http.Controller):
#     @http.route('/test_net/test_net/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/test_net/test_net/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('test_net.listing', {
#             'root': '/test_net/test_net',
#             'objects': http.request.env['test_net.test_net'].search([]),
#         })

#     @http.route('/test_net/test_net/objects/<model("test_net.test_net"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('test_net.object', {
#             'object': obj
#         })
