# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Clients(models.Model):
	_name = 'school_net.clients'
	_rec_name = "sn_client"
	_description = "API Clients"
	
	sn_client = fields.Char("Client")
	sn_key = fields.Char("Key")
	sn_isActive = fields.Boolean("is Active")
