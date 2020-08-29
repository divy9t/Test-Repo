from odoo import models, fields, api

class Activities(models.Model):
	_name = 'school_net.activities'
	_description = 'Call Activities'
	_order = 'id desc'
	_rec_name = 'sn_campaignName'

	sn_activityType = fields.Selection([('First Call','First Call'), ('Call In','Call In'), ('Call Out','Call Out'), ('Add To Campaign','Add To Campaign'),('SMS','SMS')],"Activity Type")
	sn_subject = fields.Char("Subject")
	sn_campaignName = fields.Char("Campaign Name")
	sn_start = fields.Datetime("Start")
	sn_end = fields.Datetime("End")
	sn_disposition = fields.Char("Disposition")
	sn_audioFile = fields.Char("Audio File")
	sn_comments = fields.Char("Comments")
	sn_status = fields.Selection([('',''),('Answered','Answered'),('NotAnswered','NotAnswered'),('online','online')],"Status")
	sn_agentId = fields.Char("Agent Id")
	sn_duration = fields.Char("Duration")

	sn_partnerId = fields.Many2one("res.partner","Contact")
	sn_employeeId = fields.Many2one("hr.employee","Agent",compute="_compute_employee")

	def _compute_employee(self):
		for record in self:
			record.sn_employeeId = False
			if record.sn_agentId:
				employee = self.env['hr.employee'].sudo().search([('barcode','=',record.sn_agentId)], limit=1)
				if employee:
					record.sn_employeeId = employee.id
			