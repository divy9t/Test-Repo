from odoo import http
from odoo.http import request
import json
import datetime


class SchoolNet(http.Controller):
	
	@http.route('/messageStatus',type="http", auth="public", methods=['POST'], website=True, csrf=False)
	def MessageStatus(self,data={}, **kwargs):
		data = eval(data)
		if data.get('Apikey',False):
			key = data['Apikey']
			client = request.env['school_net.clients'].sudo().search([('sn_key','=',key),('sn_isActive','=',True)], limit=1)
			if client:
				if data.get("Location",False) and data.get("Recipient",False) and data.get("MessageType",False) and data.get("SentTime",False) and data.get("DeliveredOn",False) and data.get("Status",False):
					record = request.env['school_net.messages'].sudo().create({
							"sn_recipient": data["Recipient"],
							"sn_messageType": data["MessageType"],
							"sn_sentTime": data["SentTime"],
							"sn_deliverdOn": data["DeliveredOn"],
							"sn_location": data["Location"],
							"sn_status": data["Status"]
						})
					if record:
						return json.dumps({
							"status": "success",
							"message": "Successful Sync"
						})
					else:
						return json.dumps({
							"status": "failed",
							"message": "failed to create the record"
							})
				else:
					return json.dumps({
						"status": "failed",
						"message": "Some parameters where not specified"
					})
			else:
				return json.dumps({
						"status": "failed",
						"message": "Invalid API Key, authorization failed"
					})
		else:
			return json.dumps({
					"status": "failed",
					"message": "API key not found in request"
				})

	@http.route('/callDetails', type='http', auth="public", methods=['POST'], website=True, csrf=False)
	def CallStatus(self,data={} , **kwargs):
		data = eval(data)
		if data.get('Apikey',False):
			key = data['Apikey']
			client = request.env['school_net.clients'].sudo().search([('sn_key','=',key),('sn_isActive','=',True)], limit=1)
			
			dataPoints = ['AgentPhoneNumber',"Disposition","CallerConfAudioFile","TransferredTo","Apikey","Did","StartTime","CallDuration","EndTime","ConfDuration","CustomerStatus","TimeToAnswer","monitorUCID","AgentID","AgentStatus","Location","FallBackRule","CampaignStatus","CallerID","Duration","Status","AgentUniqueID","UserName","HangupBy","AudioFile","PhoneName","TransferType","DialStatus","CampaignName","UUI","AgentName","Skill","DialedNumber","Type","Comments"]

			if client:
				if dataPoints.sort() == list(data.keys()).sort():
					fields = [x for x in request.env['school_net.calls'].sudo()._fields]
					recordData = {"sn_%s"%(x):data[x] for x in data.keys() if 'sn_%s'%(x) in fields}
					record = request.env['school_net.calls'].sudo().create(recordData)
					if record:
						return json.dumps({
							"status": "success",
							"message": "Successful Sync"
						})
					else:
						return json.dumps({
							"status": "failed",
							"message": "failed to create the record"
							})
				else:
					return json.dumps({
						"status": "failed",
						"message": "Some parameters where not specified"
					})
			else:
				return json.dumps({
						"status": "failed",
						"message": "Invalid API Key, authorization failed"
					})
		else:
			return json.dumps({
					"status": "failed",
					"message": "API key not found in request"
				})

	