# -*- coding: utf-8 -*-
# Copyright (c) 2019, August Infotech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from datetime import datetime, timedelta
from frappe.utils import flt, cint, cstr, add_days, getdate, get_datetime, get_time
from frappe import _
import frappe.defaults
from frappe import _
from frappe.model.document import Document
from frappe.utils.password import get_decrypted_password

class TenantOrder(Document):

	def validate(self):
		# set indicator color on save
		style_dict = {"Success":"Green","Danger":"Red","Inverse":"Black","Primary":"Dark Blue","Info":"Light Blue","Warning":"Orange"}
		state_style = frappe.db.get_value("Workflow State",self.workflow_state,"style")
		style_indicator = style_dict[state_style].lower()
		self.indicator_color = style_indicator
		frappe.db.set_value("Tenant Order",self.name,"indicator_color",style_indicator)
		frappe.db.commit()

		customer = frappe.db.get_value("User", {"email":str(frappe.session.user)}, "first_name")
		
		if not self.customer:
			# Set customer
			self.customer = customer
			frappe.db.set_value("Tenant Order", self.name, "customer", customer)
			frappe.db.commit()
		
			# Set customer name
			self.customer_name = frappe.db.get_value("Customer", customer, "customer_name")
			frappe.db.set_value("Tenant Order", self.name, "customer_name", frappe.db.get_value("Customer", customer, "customer_name"))
			frappe.db.commit()

		default_tenant_employee = frappe.db.get_value("Unlimited Settings", None, "default_tenant_employee")
		

		if not self.employee:
			# Set employee
			self.employee = default_tenant_employee
			frappe.db.set_value("Tenant Order", self.name, "employee", default_tenant_employee)
			frappe.db.commit()

			# Set employee name
			self.employee_name = frappe.db.get_value("Employee", default_tenant_employee, "employee_name")
			frappe.db.set_value("Tenant Order", self.name, "employee_name", frappe.db.get_value("Employee", default_tenant_employee, "employee_name"))
			frappe.db.commit()

			# Set employee duration
			self.duration = frappe.db.get_value("Employee", default_tenant_employee, "time_per_appointment")
			frappe.db.set_value("Tenant Order", self.name, "duration", frappe.db.get_value("Employee", default_tenant_employee, "time_per_appointment"))
			frappe.db.commit()

		enter_credit_card_details(self)

		# Assign task to default sales employee
		if self.workflow_state == "Debug Scan with Client": 
			assign_task_to_sales_employee(self)

		if not self.appointment_time:
			self.appointment_time = self.available_time_slot
			frappe.db.set_value("Tenant Order", self.name, "duration", frappe.db.get_value("Employee", default_tenant_employee, "time_per_appointment"))
			frappe.db.commit()

	def after_insert(self):
		# Assign task to default modelar employee
		assign_task_to_modeler_employee(self)

# ---------------------------------------------------------------------------
# Enter Credit Card Details Into Customer
# --------------------------------------------------------------------------- */
def enter_credit_card_details(self):
	frappe.db.set_value("Customer",str(frappe.db.get_value("Customer",{"customer_name":self.customer},"name")),"name_on_card",self.name_on_card)
	frappe.db.set_value("Customer",str(frappe.db.get_value("Customer",{"customer_name":self.customer},"name")),"credit_card_number",self.credit_card_number)
	frappe.db.set_value("Customer",str(frappe.db.get_value("Customer",{"customer_name":self.customer},"name")),"expiry_month",self.expiry_month)
	frappe.db.set_value("Customer",str(frappe.db.get_value("Customer",{"customer_name":self.customer},"name")),"expiry_year",self.expiry_year)
	# frappe.db.set_value("Customer",str(frappe.db.get_value("Customer",{"customer_name":self.customer},"name")),"upload_document",self.upload_document)
	customer_doc=frappe.get_doc("Customer",str(frappe.db.get_value("Customer",{"customer_name":self.customer},"name")))
	customer_doc.flags.ignore_permissions = True
	customer_doc.save()
	frappe.db.commit()
	

# ---------------------------------------------------------------------------
# Assign task to modeler employee
# --------------------------------------------------------------------------- */
def assign_task_to_modeler_employee(self):
	# default_tenant_employee = frappe.db.get_value("Unlimited Settings", None, "default_tenant_employee")
	employee_user_id = frappe.db.get_value("Employee", self.employee, "user_id")
	
	if not frappe.db.get_value("ToDo", {"owner":str(employee_user_id),"reference_type": "Tenant Order","reference_name": str(self.name)},"name"):

		# Assign ToDo to Tenant Employee
		ToDo = frappe.get_doc({
					"doctype":"ToDo",
					"status":"Open",
					"priority":"Medium",
					"date": str(self.appointment_date),
					"owner":str(employee_user_id),
					"description": str(self.customer),
					"reference_type": "Tenant Order",
					"reference_name": str(self.name),
					"assigned_by": "Administrator",
					"assigned_by_full_name": "Administrator"
				})
		ToDo.flags.ignore_permissions = True
		ToDo.insert()

# ---------------------------------------------------------------------------
# Assign task to sales employee
# --------------------------------------------------------------------------- */
def assign_task_to_sales_employee(self):
	# default_tenant_employee = frappe.db.get_value("Unlimited Settings", None, "default_tenant_sales_employee")
	employee_user_id = frappe.db.get_value("Employee", self.employee, "user_id")

	# Assign ToDo to Tenant Employee
	ToDo = frappe.get_doc({
				"doctype":"ToDo",
				"status":"Open",
				"priority":"Medium",
				"date": str(self.appointment_date),
				"owner":str(employee_user_id),
				"description": str(frappe.db.get_value("Employee", self.employee, "employee_name")),
				"reference_type": "Tenant Order",
				"reference_name": str(self.name),
				"assigned_by": "Administrator",
				"assigned_by_full_name": "Administrator"
			})
	ToDo.flags.ignore_permissions = True
	ToDo.insert()

# Get available timeslot by employee and date.
@frappe.whitelist(allow_guest=True)
def get_availability_data(date, employee):
	"""
	Get availability data of 'Employee' on 'date'
	:param date: Date to check in schedule
	:param employee: Name of employee
	:param service: Duration of service
	:return: dict containing a list of available slots, list of appointments and duration of service
	"""

	date = getdate(date)
	weekday = date.strftime("%A")

	available_slots = []
	employee_schedule_name = None
	employee_schedule = None
	employee_appointment_durations = None
	employee_holiday_name = None
	branch_holiday_name = None

	# if branch holiday return
	employee_branch = frappe.db.get_value("Employee", employee, "branch")
	branch_holiday_name = frappe.db.get_value("Branch", employee_branch, "default_holiday_list")
	if branch_holiday_name:
		branch_holidays = frappe.get_doc("Holiday List", branch_holiday_name)

		if branch_holidays:
			for t in branch_holidays.holidays:
				if t.holiday_date == date:
					frappe.msgprint(_("Barber / Beautician not available on <b>{0}</b> as it's a <b>Holiday</b>").format(datetime.strptime(cstr(date), '%Y-%m-%d').strftime('%d-%m-%Y')), _('Holiday'), 'red')

	# if employee holiday return
	employee_holiday_name = frappe.db.get_value("Employee", employee, "holiday_list")
	if employee_holiday_name:
		employee_holidays = frappe.get_doc("Holiday List", employee_holiday_name)

		if employee_holidays:
			for t in employee_holidays.holidays:
				if t.holiday_date == date:
					frappe.msgprint(_("Employee not available on <b>{0}</b> as it's a <b>Holiday</b>").format(datetime.strptime(cstr(date), '%Y-%m-%d').strftime('%d-%m-%Y')), _('Holiday'), 'red')

	# if employee on leave return
	leave_application_list = frappe.db.sql("""SELECT * FROM `tabLeave Application` WHERE `tabLeave Application`.status = 'Approved' AND `tabLeave Application`.employee = %s AND (%s BETWEEN `tabLeave Application`.from_date AND `tabLeave Application`.to_date)""" ,(cstr(employee), cstr(date)),as_dict = 1)

	if leave_application_list and len(leave_application_list) > 0:
		frappe.msgprint(_("Employee is on leave on <b>{0}</b>.").format(datetime.strptime(cstr(date), '%Y-%m-%d').strftime('%d-%m-%Y')), _('On Leave'), 'red')

	# get barber's schedule
	employee_schedule_name = frappe.db.get_value("Employee", employee, "daily_schedule_list")
	if employee_schedule_name:
		employee_schedule = frappe.get_doc("Employee Schedule", employee_schedule_name)
		employee_appointment_durations = frappe.db.get_value("Employee", employee, "time_per_appointment")
	else:
		frappe.msgprint(_("Employee {0} does not have a Employee Schedule. Add it in Employee master".format(employee)), _('Add employee schedule'),'red')

	if employee_schedule:
		for t in employee_schedule.time_slots:
			if weekday == t.day:
				available_slots.append(t)

	if not employee_appointment_durations:
		frappe.msgprint(_('"Time per appointment" hasn"t been set for <b>{0}</b>. Add it in Item master.').format(employee), _('Add time per appointment'),'red' )

	# if employee not available return
	if not available_slots:
		frappe.msgprint(_("Employee not available on {0}").format(weekday), _('Not available'),'red')

	# get appointments on that day for employee
	appointments = frappe.get_all(
		"Tenant Order",
		filters={"employee": employee, "appointment_date": date},
		fields=["name", "appointment_time", "duration", "workflow_state"])

	return {
		"available_slots": available_slots,
		"appointments": appointments,
		"duration_of_service": employee_appointment_durations
	}

# Get end time of the day for barber.
@frappe.whitelist()
def get_day_end_time(date, employee):
	"""
	Get end time of 'Employee' on 'date'
	:param date: Date to check in schedule
	:param employee: Name of employee
	:return: end time of the given date
	"""
	employee_schedule_name = frappe.db.get_value("Employee", employee, "daily_schedule_list")
	date = getdate(date)
	weekday = date.strftime("%A")
	
	get_end_time = frappe.db.sql("""SELECT Max(`tabEmployee Schedule Time Slot`.to_time) as day_end_time FROM `tabEmployee Schedule` LEFT JOIN `tabEmployee Schedule Time Slot` ON `tabEmployee Schedule`.name = `tabEmployee Schedule Time Slot`.parent WHERE `tabEmployee Schedule`.name = %s AND `tabEmployee Schedule Time Slot`.day = %s""" ,(cstr(employee_schedule_name),cstr(weekday)),as_dict = 1)
	if get_end_time and len(get_end_time) > 0:
		return cstr(get_end_time[0]['day_end_time'])

@frappe.whitelist(allow_guest=True)
def get_available_slots(date, employee):
	date = getdate(date)
	weekday = date.strftime("%A")

	available_slots = []
	employee_schedule_name = None
	employee_schedule = None
	employee_appointment_durations = None
	employee_holiday_name = None
	branch_holiday_name = None
	is_holiday = 'No'
	is_on_leave = 'No'
	has_employee_schedule = 'Yes'
	has_employee_time_per_appointment = 'Yes'
	is_employee_available = 'Yes'

	# if branch holiday return
	employee_branch = frappe.db.get_value("Employee", employee, "branch")
	branch_holiday_name = frappe.db.get_value("Branch", employee_branch, "default_holiday_list")
	if branch_holiday_name:
		branch_holidays = frappe.get_doc("Holiday List", branch_holiday_name)

		if branch_holidays:
			for t in branch_holidays.holidays:
				if t.holiday_date == date:
					is_holiday = 'Yes'

	# if employee holiday return
	employee_holiday_name = frappe.db.get_value("Employee", employee, "holiday_list")
	if employee_holiday_name:
		employee_holidays = frappe.get_doc("Holiday List", employee_holiday_name)

	if employee_holidays:
		for t in employee_holidays.holidays:
			if t.holiday_date == date:
				is_holiday = 'Yes'

	# if employee on leave return
	leave_application_list = frappe.db.sql("""SELECT * FROM `tabLeave Application` WHERE `tabLeave Application`.status = 'Approved' AND `tabLeave Application`.employee = %s AND (%s BETWEEN `tabLeave Application`.from_date AND `tabLeave Application`.to_date)""" ,(cstr(employee), cstr(date)),as_dict = 1)

	if leave_application_list and len(leave_application_list) > 0:
		is_on_leave = 'Yes'

	# get barber's schedule
	employee_schedule_name = frappe.db.get_value("Employee", employee, "daily_schedule_list")
	if employee_schedule_name:
		employee_schedule = frappe.get_doc("Employee Schedule", employee_schedule_name)
		employee_appointment_durations = frappe.db.get_value("Employee", employee, "time_per_appointment")
	else:
		has_employee_schedule = 'No'

	if employee_schedule:
		for t in employee_schedule.time_slots:
			if weekday == t.day:
				available_slots.append(t)

	if not employee_appointment_durations:
		has_employee_time_per_appointment = 'No'

	# if employee not available return
	if not available_slots:
		is_employee_available = 'No'

	# get appointments on that day for employee
	appointments = frappe.get_all(
	"Tenant Order",
	filters={"employee": employee, "appointment_date": date},
	fields=["name", "appointment_time", "duration", "workflow_state"])

	return {
	"available_slots": available_slots,
	"appointments": appointments,
	"duration_of_service": employee_appointment_durations,
	"is_holiday": is_holiday,
	"is_on_leave":is_on_leave,
	"has_employee_schedule": has_employee_schedule,
	"has_employee_time_per_appointment": has_employee_time_per_appointment,
	"is_employee_available": is_employee_available
	}

@frappe.whitelist(allow_guest=True)
def get_default_employee():
	return cstr(frappe.db.get_value("Unlimited Settings", None, "default_tenant_employee"))

@frappe.whitelist(allow_guest=True)
def get_credit_card_info(user):
	customer=cstr(frappe.db.get_value("User", {"email":user}, "first_name"))
	customer_id=cstr(frappe.db.get_value("Customer", {"customer_name":customer}, "name"))

	return{
		"customer":customer,
		"name":cstr(get_decrypted_password('Customer',customer_id,'name_on_card',False)),
		"card_number":cstr(get_decrypted_password('Customer',customer_id,'credit_card_number',False)),
		"ex_month":cstr(get_decrypted_password('Customer',customer_id,'expiry_month',False)),
		"ex_year":cstr(get_decrypted_password('Customer',customer_id,'expiry_year',False))
	}
