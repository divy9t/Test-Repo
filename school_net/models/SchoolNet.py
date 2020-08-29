# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SchoolNet(models.Model):
	_name = 'school_net.school_net'
	_rec_name = "name"

	name = fields.Char("Name")