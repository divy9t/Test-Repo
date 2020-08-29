from odoo import models, fields, api
from odoo.http import request
from datetime import datetime
from datetime import timedelta
import requests
from requests.auth import HTTPBasicAuth

class Skills(models.Model):
	_name = 'school_net.skills'
	_activity_name = 'Skills Exchange Sync'
	_description = 'Pravasi Skills Exchange'
	
	def _cron_api_call(self):
		#parameters
		start_date = (datetime.now()+ timedelta(days=-1))
		end_date = datetime.now()
		model = self.env['school_net.log'].sudo()
		url = self.env["ir.config_parameter"].sudo().get_param("school_net.skills_api")
		username = self.env["ir.config_parameter"].sudo().get_param("school_net.skills_username")
		password = self.env["ir.config_parameter"].sudo().get_param("school_net.skills_password")

		limit = int(self.env["ir.config_parameter"].sudo().get_param("school_net.skills_limit"))
		skip = 0
		
		headers = {'Content-Type': 'application/json'}
		while False:
			query = """
				{
					crmGetUpdatedCandidates(
						fromDate: "%s"
						toDate: "%s"
						skip: %d
						limit: %d
						) 
					{
						totalCandidates
						candidates {
							id
							firstName
							isSelfIntroUpdated
							lastName
							gender
							category
							mobile
							email
							isMobileVerified
							counsellingRequired
							source
							employmentPreference
							creatorRole
							district
							state
							fresherOrExperienced
							areEducationDetailsUpdated
							arePreferredLocationsUpdated
							arePreferredCategoriesUpdated
							areEmploymentHistoriesUpdated
							createdTimeStamp
							updatedTimeStamp

						}
						
					}
				}
				"""%(start_date.strftime("%Y-%m-%dT%H:%M:%S"), end_date.strftime("%Y-%m-%dT%H:%M:%S"), skip, limit )
			
			try:
				request = requests.post(url, json={'query': query}, headers=headers,auth=HTTPBasicAuth(username, password), verify=False)
				if request.status_code == 200:
					data = request.json()
					if data.get("errors",False):
						model.create({
							'sn_Activity': self._activity_name,
							'sn_Message':  'Error while connecting to API, %s'%(' | '.join([x['message'] for x in data['errors']])),
							'sn_Status': False
							})
						break
					else:
						records = data['data']['crmGetUpdatedCandidates']['candidates']
						createdRecords = 0
						updateRecords = 0
						for contact in records:
							createRecord = True
							state = self.env['res.country.state'].sudo().search([("name","=",contact['state'])],limit=1)
							country = self.env['res.country'].sudo().search([("name","=","India")],limit=1)
							mobile_details = contact['mobile'][-10:] if contact['mobile'] else ''
								
							if contact.get('id',False):
								partner = self.env['res.partner'].sudo().search([('sn_skillsExchangeId','=',int(contact['id']))], limit = 1)
								if partner:
									partner.write({
											'name': "%s %s"%(contact['firstName'], contact['lastName']),
											'mobile': mobile_details,
											'phone': mobile_details,
											'email': contact['email'],
											'sn_skillsExchangeId': contact['id'],
											'sn_counsellingRequired': contact['counsellingRequired'],
											'sn_employmentPreference': contact['employmentPreference'],
											'sn_creatorRole': contact['creatorRole'],
											'sn_gender': contact['gender'],
											'sn_category': contact['category'],
											'sn_source': contact['source'],
											'sn_Experience': contact['fresherOrExperienced'],
											'sn_isSelfIntroUpdated': contact['isSelfIntroUpdated'],
											'sn_isMobileVerified': contact['isMobileVerified'],
											'sn_areEducationDetailsUpdated': contact['areEducationDetailsUpdated'],
											'sn_arePreferredLocationsUpdated': contact['arePreferredLocationsUpdated'],
											'sn_arePreferredCategoriesUpdated': contact['arePreferredCategoriesUpdated'],
											'sn_areEmploymentHistoriesUpdated': contact['areEmploymentHistoriesUpdated'],
											'city': contact['district'],
											'state_id': state.id,
											'country_id': country.id,
										})
									updateRecords += 1
									createRecord = False

							if createRecord:
								exitingPartner = self.env['res.partner'].sudo().search(['|',('phone','=', mobile_details),('mobile','=',mobile_details)], limit=1)
								if exitingPartner:
									exitingPartner.write({
											'name': "%s %s"%(contact['firstName'], contact['lastName']),
											'mobile': mobile_details,
											'phone': mobile_details,
											'email': contact['email'],
											'sn_skillsExchangeId': contact['id'],
											'sn_counsellingRequired': contact['counsellingRequired'],
											'sn_employmentPreference': contact['employmentPreference'],
											'sn_creatorRole': contact['creatorRole'],
											'sn_gender': contact['gender'],
											'sn_category': contact['category'],
											'sn_source': contact['source'],
											'sn_Experience': contact['fresherOrExperienced'],
											'sn_isSelfIntroUpdated': contact['isSelfIntroUpdated'],
											'sn_isMobileVerified': contact['isMobileVerified'],
											'sn_areEducationDetailsUpdated': contact['areEducationDetailsUpdated'],
											'sn_arePreferredLocationsUpdated': contact['arePreferredLocationsUpdated'],
											'sn_arePreferredCategoriesUpdated': contact['arePreferredCategoriesUpdated'],
											'sn_areEmploymentHistoriesUpdated': contact['areEmploymentHistoriesUpdated'],
											'city': contact['district'],
											'state_id': state.id,
											'country_id': country.id,
										})
									updateRecords += 1
								else:
									self.env['res.partner'].sudo().create({
										'name': "%s %s"%(contact['firstName'], contact['lastName']),
										'mobile': mobile_details,
										'phone': mobile_details,
										'email': contact['email'],
										'sn_skillsExchangeId': contact['id'],
										'sn_counsellingRequired': contact['counsellingRequired'],
										'sn_employmentPreference': contact['employmentPreference'],
										'sn_creatorRole': contact['creatorRole'],
										'sn_gender': contact['gender'],
										'sn_category': contact['category'],
										'sn_source': contact['source'],
										'sn_Experience': contact['fresherOrExperienced'],
										'sn_isSelfIntroUpdated': contact['isSelfIntroUpdated'],
										'sn_isMobileVerified': contact['isMobileVerified'],
										'sn_areEducationDetailsUpdated': contact['areEducationDetailsUpdated'],
										'sn_arePreferredLocationsUpdated': contact['arePreferredLocationsUpdated'],
										'sn_arePreferredCategoriesUpdated': contact['arePreferredCategoriesUpdated'],
										'sn_areEmploymentHistoriesUpdated': contact['areEmploymentHistoriesUpdated'],
										'city': contact['district'],
										'state_id': state.id,
										'country_id': country.id,
										'sn_createSource': 'Skills Exchange'
									})
									createdRecords += 1
						model.create({
							'sn_Activity': self._activity_name,
							'sn_Message':  'Synced records from API',
							'sn_RecordsCreated': createdRecords,
							'sn_RecordsUpdated': updateRecords,
							'sn_Status': True
						})
						break
						if data['data']['crmGetUpdatedCandidates']['totalCandidates'] < limit:
							break
			except Exception as e:
				model.create({
							'sn_Activity': self._activity_name,
							'sn_Message':  'Error while requesting API, Error: %s'%(str(e)),
							'sn_Status': False
						})
				break

			

			skip += limit