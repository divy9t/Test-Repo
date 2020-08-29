
from odoo import models, fields, api
from ast import literal_eval

import datetime
import logging

_logger = logging.getLogger(__name__)

class Campaign(models.Model):
	_name = 'school_net.campaign'
	_rec_name = 'sn_name'
	_order = 'id desc'
	_description = 'Pravasi Campaign'
	_activity_name = "Pravasi Campaign"

	sn_name = fields.Char("Campaign Name")
	sn_description = fields.Char("Campaign Description")
	sn_ActivityNote = fields.Char("Activity Note")
	sn_activityType = fields.Selection([('First Call','First Call'), ('Call In','Call In'), ('Call Out','Call Out'), ('Add To Campaign','Add To Campaign'),('SMS','SMS')],"Activity Type")

	sn_createCallingList = fields.Boolean("Create Calling List")
	sn_contactDomain = fields.Char("Callout Rule", help="Domain to filter contacts")
	sn_exclusionPeriodFrequency = fields.Char("Exclusion Period (Days)")

	def _cron_api_call(self):
		model = self.env['school_net.log'].sudo()		

		campaigns_to_process = self.search([('sn_createCallingList','=',True)])

		if not campaigns_to_process:
			model.create({
						'sn_Activity': self._activity_name,
						'sn_Message':  'No Campaign to process and create lists for, please create a campaign with \'Create Calling List\' parameter as true.',
						'sn_Status': False
					})
			return False

		for campaign in campaigns_to_process:
			try:
				domain = literal_eval(campaign.sn_contactDomain)
				contacts = self.env['res.partner'].sudo().search(domain)

				exclusion_date = datetime.datetime.now() - datetime.timedelta(days=int(campaign.sn_exclusionPeriodFrequency))
				contact_activities = self.env['school_net.activities'].sudo().search([('sn_campaignName','=', campaign.sn_name),('sn_partnerId','in',contacts.ids), ('sn_start','>',exclusion_date)])

				contact_ids = set(contacts.ids) - set(contact_activities.mapped('sn_partnerId').ids)
				contacts_to_push = self.env['res.partner'].sudo().browse(contact_ids)

				if contacts_to_push:
					callout_list_records = [(0,0,{'sn_contactId':contact.id, 'sn_contactNumber': contact.phone or contact.mobile, 'sn_pushStatus':'Pending Sync'}) for contact in contacts_to_push]
					bulk_data_record = self.env['school_net.callout_list'].sudo().create({
						'sn_calloutListLines':callout_list_records,
						'sn_campaignName':campaign.sn_name
						})
					model.create({
						'sn_Activity': self._activity_name,
						'sn_Message':  'Campaign callout list created with %d records'%(len(callout_list_records)),
						'sn_Status': True
					})
			except Exception as e:
				model.create({
						'sn_Activity': self._activity_name,
						'sn_Message':  'Error while creating Campaign Callout list, Error: %s'%(str(e)),
						'sn_Status': False
					})
