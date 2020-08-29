from odoo import models, fields, api
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class Skills(models.Model):
	_inherit = "res.partner"

	sn_skillsExchangeId = fields.Integer("Skills Exchange ID")
	sn_counsellingRequired = fields.Char("Counselling Required")
	sn_employmentPreference = fields.Char("Employment Preference")
	sn_creatorRole = fields.Char("Creator Role")
	sn_createSource = fields.Char("Channel")

	sn_gender = fields.Selection([("Male","Male"),("Female", "Female"),("Others","Others")],"Gender")
	sn_category = fields.Char("Category")
	sn_source = fields.Char("Source")
	sn_Experience = fields.Char("Fresher Or Experienced")
	
	sn_isSelfIntroUpdated = fields.Boolean("Counselling Required")
	sn_isMobileVerified = fields.Boolean("Mobile Verified")
	sn_areEducationDetailsUpdated = fields.Boolean("Education Details")
	sn_arePreferredLocationsUpdated = fields.Boolean("Preferred Locations")
	sn_arePreferredCategoriesUpdated = fields.Boolean("Preferred Categories")
	sn_areEmploymentHistoriesUpdated = fields.Boolean("Employment Histories")
	
	sn_activityCount = fields.Integer("Activities", compute="_compute_Activities")
	sn_createDate = fields.Datetime("Creation Date")

	def _compute_Activities(self):
		for record in self:
			record.sn_activityCount = self.env['school_net.activities'].sudo().search_count([('sn_partnerId','=',record.id)])
	

	def _cron_api_call(self):
		partners = self.search(["&","&",("sn_bulkPushStatus","!=",False),("sn_skillsExchangeId","!=",False),('sn_bulkPushStatus','!=','Sent & Deleted')], limit=500)
		client = self.env['school_net.clients'].sudo().search([('sn_isActive','=',True)], limit=1)
		if not client:
			_logger.info("API Key not present")
			return False

		if not client:
			_logger.info("API Config is not set properly")
			return False

		for partner in partners:
			headers = {'Content-Type': 'application/json'}
			delete_data = '''
			{
			'api_key':%s,
			'user_name':%s,
			'campaign_name':%s,
			'caller_number':%s,
			'validate'=true,
			}
			'''

			request = requests.post(api_data.sn_apiUrl, data = delete_data%(client.sn_key, api_data.sn_cloudAgentUserName, api_data.sn_campaignName, partner.mobile or partner.phone), headers=headers)
			if request.status_code == 200:
				data = request.json()
				if data.get('status') == "success" and data.get('message') == "Deleted Successfully":
					partner.sn_bulkPushStatus == "Sent & Deleted"
					bulk_line = self.env['school_net.contact_bulk_data_line'].sudo().search([('sn_contactId','=',partner.id)], limit=1).write({'sn_pushStatus':'Sent & Deleted'})
					_logger.info("Contact Record successfully removed from ozonetel bulk data")
				else:
					_logger.info("Contact couldn't be deleted because %s"%(data.get('message')))

			else:
				_logger.info("There was a problem sending the delete request")
