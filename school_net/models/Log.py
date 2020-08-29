from odoo import models, fields, api

class Skills(models.Model):
	_name = 'school_net.log'
	_rec_name = 'sn_Activity'
	_order = 'id desc'
	_description = 'Pravasi Logs'
	
	sn_Activity = fields.Char("Activity")
	sn_Message = fields.Char("Message")
	sn_RecordsCreated = fields.Integer("Created")
	sn_RecordsUpdated = fields.Integer("Updated")
	sn_Status = fields.Boolean('Sucess')