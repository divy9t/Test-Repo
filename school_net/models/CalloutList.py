from odoo import models, fields, api
from odoo.http import request
from datetime import datetime
from datetime import timedelta
import requests
from urllib.parse import urlencode
from collections import OrderedDict
from requests.auth import HTTPBasicAuth
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class CalloutList(models.Model):
	_name = 'school_net.callout_list'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_description = "Campaign Callout List"
	_activity_name = "Campaign Callout List"
	_rec_name = "sn_name"

	sn_name = fields.Char("Name",default="New")
	sn_calloutListLines = fields.One2many('school_net.callout_list_line','sn_calloutList',string="Pushed Records")
	sn_campaignName = fields.Char("Campaign Name")
	sn_status = fields.Selection([('In progress','In progress'),('Success','Success'),('Failure','Failure'),('Warning','Warning')], string="Status", compute="_compute_status")

	@api.depends('sn_calloutListLines')
	def _compute_status(self):
		for record in self:
			all_success = all(list(map(lambda line: True if line.sn_pushStatus == "Synced"  else False, record.sn_calloutListLines)))
			all_failed = all(list(map(lambda line: True if line.sn_pushStatus == "Failed"  else False, record.sn_calloutListLines)))
			in_progress = any(list(map(lambda line: True if line.sn_pushStatus == "Pending Sync"  else False, record.sn_calloutListLines)))
			warning = any(list(map(lambda line: True if line.sn_pushStatus == "Failed"  else False, record.sn_calloutListLines))) and any(list(map(lambda line: True if line.sn_pushStatus == "Synced"  else False, record.sn_calloutListLines)))
			
			if all_success:
				record.sn_status = "Success"
			elif all_failed:
				record.sn_status = "Failure"
			elif warning:
				record.sn_status = "Warning"
			elif in_progress:
				record.sn_status = "In progress"
			else:
				record.sn_status = False


	@api.model	
	def create(self, vals):
		vals['sn_name'] = self.env['ir.sequence'].next_by_code('school_net.callout_list_sequence')
		rec = super(CalloutList, self).create(vals)
		return rec

	def _push_data(self):
		for record in self:
			records_to_push = record.mapped('sn_calloutListLines').filtered(lambda line: line.sn_pushStatus == 'Failed' or line.sn_pushStatus == 'Pending Sync')
			if records_to_push:
				records_to_push = records_to_push[0:int(self.env["ir.config_parameter"].sudo().get_param("school_net.api_rec_num"))]
				push_status = self.env['school_net.callout_list_line']._push_data(records_to_push, record.sn_campaignName)
				if push_status:
					model = self.env['school_net.log'].sudo()
					model.create({
						'sn_Activity': self._activity_name,
						'sn_Message':  'Manually Synced %d records'%(len(records_to_push)),
						'sn_Status': True
					})






class CalloutListLine(models.Model):
	_name = 'school_net.callout_list_line'
	_description = "Campaign Callout List Line"
	_activity_name = "Campaign Callout List Line"

	sn_contactId = fields.Many2one('res.partner','Contact')
	sn_contactNumber = fields.Char("Contact Number")
	sn_pushStatus = fields.Selection([('Pending Sync','Pending Sync'),('Synced','Synced'),('Failed','Failed')],"Status")
	sn_calloutList = fields.Many2one('school_net.callout_list', string="Bulk Record Id")

	def _cron_api_call(self):	
		#Fetching the contacts from the record which needs to be pushed to server
		callout_list_lines = self.search([('sn_pushStatus','=','Pending Sync')],limit=int(self.env["ir.config_parameter"].sudo().get_param("school_net.api_rec_num")), order="id desc")

		#Creating data to be pushed
		records_to_push = list(map(lambda contact: [contact.sn_contactNumber, "Jorhat"],callout_list_lines))

		if not records_to_push:
			self.env['school_net.log'].sudo().create({
						'sn_Activity': self._activity_name,
						'sn_Message':  'No callout records list to push',
						'sn_Status': False
					})
			return False


		campaign_contact_dict = {}
		for contact in callout_list_lines:
			if contact.sn_calloutList.sn_campaignName:
				campaign_contact_dict.setdefault(contact.sn_calloutList.sn_campaignName,[]).append(contact)

		for key, value in campaign_contact_dict.items():
			self._push_data(value, key)
		


	def _push_data(self,callout_list_lines,campaign_name):
		# Model for logging
		model = self.env['school_net.log'].sudo()		

		#Fetch the api key and push url first, if they aren't present then raise error
		api_key, url = self.env["ir.config_parameter"].sudo().get_param("school_net.api_key"), self.env["ir.config_parameter"].sudo().get_param("school_net.bulk_push_api")
		records_to_push = list(map(lambda contact: [contact.sn_contactNumber, "Jorhat"],callout_list_lines))

		if not api_key or not url:
			raise ValidationError("Api key or url not present in config parameters, please set them.")
				
		#Creating the query string for post data
		query_string = urlencode(OrderedDict(api_key=api_key, campaign_name=campaign_name, bulkData={"map":["PhoneNumber","skill"],"data":records_to_push}), encoding="UTF-8")
		post_url = "%s?%s"%(url,query_string)
		post_url = post_url.replace('%27','%22')

		#api call to push data
		try:
			data_response = requests.post(post_url)

			if data_response.status_code == 200:
				data = data_response.json()

				#Checking if there is an error
				if data.get("status",False):
					model.create({
						'sn_Activity': self._activity_name,
						'sn_Message':  'Post request for url: %s, failed with message: %s'%(post_url, data.get("message",False)),
						'sn_Status': False
					})
					return False

				#iterating through message list since it can hold 
				#multiple records
				elif data.get("message",False):
					pushed_contacts = {}
					for message in data['message']:
						line_record = list(filter(lambda line: line.sn_contactNumber == message.get('PhoneNumber','2'), callout_list_lines))
						if line_record:
							if message.get('Status') == "SuccessFully Updated":
								line_record[0].write({'sn_pushStatus':'Synced'})
								activity_record = self.env['school_net.activities'].sudo().create(
								{
								'sn_activityType':'Add To Campaign',
								'sn_subject':'Contact Pushed',
								'sn_campaignName':campaign_name,
								'sn_start':datetime.now(),
								'sn_partnerId':line_record[0].sn_contactId.id
								})

								pushed_contacts.setdefault(line_record[0].sn_calloutList,0)
								pushed_contacts[line_record[0].sn_calloutList] += 1
							else:
								line_record[0].sn_pushStatus = 'Failed'



					campaignDict = {}
					for key, value in pushed_contacts.items():					
						key.message_post(body="%s record(s) pushed at %s"%(value, datetime.now()))
						campaignDict.setdefault(key.sn_campaignName,[])
						campaignDict[key.sn_campaignName].append(value)


					model.create({
						'sn_Activity': self._activity_name,
						'sn_Message':  'Post request successful for campaign(s) %s, pushing %s record(s) respectively'%(','.join([x for x in campaignDict.keys()]),','.join([str(sum(x)) for x in campaignDict.values()])),
						'sn_Status': True
					})

					return True


				else:
					model.create({
						'sn_Activity': self._activity_name,
						'sn_Message':  'Something went wrong while hitting the post url: %s'%(post_url),
						'sn_Status': True
					})
					return False
			else:
				model.create({
						'sn_Activity': self._activity_name,
						'sn_Message':  'Post api call for: %s, returned status code:: %s'%(post_url, data_response.status_code),
						'sn_Status': False
					})
				return False
		except Exception as e:
			model.create({
						'sn_Activity': self._activity_name,
						'sn_Message':  'Error while pushing data to API, Error: %s'%(str(e)),
						'sn_Status': False
					})
			return False
	