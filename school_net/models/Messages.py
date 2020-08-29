# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class Messages(models.Model):
	_name = 'school_net.messages'
	_order = 'id desc'
	_description = 'Pravasi Message Logs'

	sn_recipient = fields.Char("Recipient")
	sn_messageType = fields.Char("message Type")
	sn_sentTime = fields.Char("Sent Time")
	sn_deliverdOn = fields.Char("Delivered On")
	sn_location = fields.Char("Location")
	sn_status = fields.Char("Status")

	@api.model
	def create(self, values):
		record = super(Messages, self).create(values)
		contact = self.env['res.partner'].sudo().search(['|',('mobile','=',record.sn_recipient[-10:]),('phone','=',record.sn_recipient[-10:])], limit=1)
		if not contact:
			contact = self.env['res.partner'].sudo().create({
				'name': record.sn_recipient[-10:],
				'phone': record.sn_recipient[-10:],
				'company_type': 'person',
				'sn_createSource': 'Message',
				'sn_createDate' : datetime.strptime(record.sn_sentTime,"%Y-%m-%d %H:%M:%S")
				})
		campaign = self.env['school_net.campaign'].sudo().search([('sn_name','=',record.sn_messageType)], limit=1)
		#Activity
		self.env['school_net.activities'].sudo().create({
				'sn_activityType': campaign.sn_activityType,
				'sn_subject': campaign.sn_ActivityNote if campaign else "Message: %s, is %s on %s"%(record.sn_messageType, record.sn_status, record.sn_sentTime),
				'sn_campaignName': record.sn_messageType,
				'sn_start': datetime.strptime(record.sn_sentTime,"%Y-%m-%d %H:%M:%S"),
				'sn_end':datetime.strptime(record.sn_deliverdOn,"%Y-%m-%d %H:%M:%S"),
				#'sn_status': record.sn_status,
				'sn_partnerId': contact.id
			})
		#contact.message_post(body=campaign.sn_ActivityNote if campaign else "Message: %s, is %s on %s"%(record.sn_messageType, record.sn_status, record.sn_sentTime))
		return record