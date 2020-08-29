# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

import os

import inspect, csv

import logging

_logger = logging.getLogger(__name__)

class Calls(models.Model):
	_name = 'school_net.calls'
	_rec_name = 'sn_DialedNumber'
	_order = 'id desc'
	_description = 'Pravasi Call Logs'

	sn_AgentPhoneNumber = fields.Char("Agent Phone Number")
	sn_Disposition = fields.Char("Disposition")
	sn_CallerConfAudioFile = fields.Char("Caller Conf Audio File")
	sn_TransferredTo = fields.Char("Transferred To")
	sn_Did = fields.Char("Did")
	sn_StartTime = fields.Char("Start Time")
	sn_CallDuration = fields.Char("Call Duration")
	sn_EndTime = fields.Char("End Time")
	sn_ConfDuration = fields.Char("Conf Duration")
	sn_CustomerStatus = fields.Char("Customer Status")
	sn_TimeToAnswer = fields.Char("Time To Answer")
	sn_monitorUCID = fields.Char("monitor UCID")
	sn_AgentID = fields.Char("Agent ID")
	sn_AgentStatus = fields.Char("Agent Status")
	sn_Location = fields.Char("Location")
	sn_FallBackRule = fields.Char("Fall Back Rule")
	sn_CampaignStatus = fields.Char("Campaign Status")
	sn_CallerID = fields.Char("Caller ID")
	sn_Duration = fields.Char("Duration")
	sn_Status = fields.Char("Status")
	sn_AgentUniqueID = fields.Char("Agent UniqueID")
	sn_UserName = fields.Char("User Name")
	sn_HangupBy = fields.Char("Hangup By")
	sn_AudioFile = fields.Char("Audio File")
	sn_PhoneName = fields.Char("Phone Name")
	sn_TransferType = fields.Char("Transfer Type")
	sn_DialStatus = fields.Char("Dial Status")
	sn_CampaignName = fields.Char("Campaign Name")
	sn_UUI = fields.Char("UUI")
	sn_AgentName = fields.Char("Agent Name")
	sn_Skill = fields.Char("Skill")
	sn_DialedNumber = fields.Char("Dialed Number")
	sn_Type = fields.Char("Type")
	sn_Comments = fields.Char("Comments")

	def _import_csv_records(self, filename=""):
		current_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
		file_path = current_path.split('\\')
		file_path.pop()
		file_path.pop()

		file_path = "%s%s"%('\\'.join(file_path),"\\%s"%(filename))
		raise Exception(file_path)

		with open(file_path) as csv_file:
			csv_reader = csv.reader(csv_file, delimiter='\t')
			col_header = next(csv_reader)
			line_count = 0
			
			for row in csv_reader:

				call_record = dict(zip(col_header, row))

				date = datetime.strptime(call_record.get('Call Date').replace('/','-'),"%m-%d-%Y").strftime("%Y-%m-%d") if call_record.get('Call Date') else False

				start_time, end_time = False, False
				if date:
					start_time = "%s %s"%(date,call_record.get('Start Time'))
					end_time = "%s %s"%(date,call_record.get('End Time'))


				if call_record.get('Status', False) == "Unanswered":
					call_record['Status'] = "NotAnswered"

				call_record_dict = {
				'sn_CallerID':call_record.get('Caller No')[-10:],
				'sn_CampaignName':call_record.get('Campaign Name', False) or call_record.get('Campaign'),
				'sn_StartTime':start_time if start_time else False ,
				'sn_EndTime':end_time if end_time else False,
				'sn_Type':call_record.get('Call Type'),
				'sn_Location':call_record.get('Location', False),
				'sn_Skill':call_record.get('Skill', False),
				'sn_TimeToAnswer':call_record.get('Time to Answer', False),
				'sn_DialStatus':call_record.get('Dial Status', False),
				'sn_Duration':call_record.get('Duration', False),
				'sn_UUI':call_record.get('UUI', False),
				'sn_UUI':call_record.get('UUI', False),
				'sn_Comments':call_record.get('comments', False),
				'sn_AudioFile':call_record.get('Audio File URL', False),
				'sn_AgentID':call_record.get('Agent', False),
				'sn_DialedNumber':call_record.get('Dialed Number', False),
				'sn_AgentStatus':call_record.get('Agent Dial Status', False),
				'sn_CustomerStatus':call_record.get('Customer Dial Status', False),
				'sn_Disposition':call_record.get('Disposition', False),
				'sn_Status':call_record.get('Status', False),
				'sn_HangupBy':call_record.get('Hangup By', False),
				'sn_Did':call_record.get('Called No')
				}
				
				call = self.create(call_record_dict)

				if line_count%200 == 0:
					_logger.info("RECORDS GETTING CREATED NO OF LINE %s"%(line_count))
				line_count += 1




	@api.model
	def create(self, values):
		record = super(Calls, self).create(values)
		if record.sn_CallerID:
			contact = self.env['res.partner'].sudo().search(['|',('mobile','=',record.sn_CallerID[-10:]),('phone','=',record.sn_CallerID[-10:])], limit=1)
			if not contact:
				contact = self.env['res.partner'].sudo().create({
					'name': record.sn_CallerID[-10:],
					'phone': record.sn_CallerID[-10:],
					'mobile': record.sn_CallerID[-10:],
					'company_type': 'person',
					'sn_createSource': "Call",
					'sn_createDate' : datetime.strptime(record.sn_StartTime,"%Y-%m-%d %H:%M:%S")
					})
			
			campaign = self.env['school_net.campaign'].sudo().search([('sn_name','=',record.sn_CampaignName)], limit=1)
			first_call = self.env['school_net.activities'].sudo().search([('sn_activityType','=','First Call'),('sn_partnerId','=', contact.id)],limit=1)			
			#Activity
			self.env['school_net.activities'].sudo().create({
					'sn_activityType': 'Call In' if first_call else campaign.sn_activityType,
					'sn_subject': campaign.sn_ActivityNote if campaign else "Called: %s"%(record.sn_CallerID),
					'sn_campaignName': record.sn_CampaignName,
					'sn_start': datetime.strptime(record.sn_StartTime,"%Y-%m-%d %H:%M:%S") ,
					'sn_end': datetime.strptime(record.sn_EndTime,"%Y-%m-%d %H:%M:%S"),
					'sn_disposition': record.sn_Disposition,
					'sn_audioFile': record.sn_AudioFile,
					'sn_status': record.sn_Status,
					'sn_agentId': record.sn_AgentID,
					'sn_partnerId': contact.id
				})
			#contact.message_post(body=campaign.sn_ActivityNote if campaign else "Called: %s"%(record.sn_CallerID))
		return record
