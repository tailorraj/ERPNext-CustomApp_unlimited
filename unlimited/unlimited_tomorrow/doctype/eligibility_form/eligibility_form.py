# -*- coding: utf-8 -*-
# Copyright (c) 2018, August Infotech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class EligibilityForm(Document):
	def validate(self):
		style_dict = {"Success":"Green","Danger":"Red","Inverse":"Black","Primary":"Dark Blue","Info":"Light Blue","Warning":"Orange"}
		state_style = frappe.db.get_value("Workflow State",self.workflow_state,"style")
		style_indicator = style_dict[state_style].lower()
		self.indicator_color = style_indicator
		frappe.db.set_value("Eligibility Form",self.name,"indicator_color",style_indicator)
		frappe.db.commit()

	def reject_request(self, args):
		frappe.db.set(self, 'rejection_reason', args["rejection_reason"])
		frappe.db.set(self, 'workflow_state', 'Rejected')
		frappe.db.commit()

		style_dict = {"Success":"Green","Danger":"Red","Inverse":"Black","Primary":"Dark Blue","Info":"Light Blue","Warning":"Orange"}
		state_style = frappe.db.get_value("Workflow State",self.workflow_state,"style")
		style_indicator = style_dict[state_style].lower()
		self.indicator_color = style_indicator
		frappe.db.set_value("Eligibility Form",self.name,"indicator_color",style_indicator)
		frappe.db.commit()
