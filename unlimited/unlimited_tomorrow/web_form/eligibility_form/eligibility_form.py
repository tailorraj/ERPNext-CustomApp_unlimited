from __future__ import unicode_literals

import frappe

# def get_context(context):
def get_context(context):
	get_permission = is_new_button_show(frappe.session.user)
	
	if get_permission == 'False':
		context.read_only = 1
	# context.show_sidebarar = 0

def get_list_context(context):
	# frappe.throw("Hello")
	context.row_template = "unlimited/templates/includes/eligibility_form/eligibility_form_list_row.html"
	context.get_list = get_eligibility_form_list

def get_eligibility_form_list(doctype, txt, filters, limit_start, limit_page_length = 20, order_by='modified desc'):
	eligibility_form = frappe.get_all("Eligibility Form", filters={
	"owner": frappe.session.user	
	}, fields=["*"], limit_page_length=10, order_by="creation desc")
	return eligibility_form

@frappe.whitelist(allow_guest=True)
def is_new_button_show(user):
	is_show = "True"
	get_form_list = frappe.db.sql("""SELECT name FROM `tabEligibility Form` WHERE owner = %s
			and workflow_state in ("Open","In Progress","Approved","Cancelled")""", (str(user)), as_dict = 1)
	if get_form_list:
		if len(get_form_list) > 0:
			is_show = "False"

	return is_show

@frappe.whitelist(allow_guest=True)
def has_approved_form(user):
	has_approved_form = "False"
	get_form_list = frappe.db.sql("""SELECT name FROM `tabEligibility Form` WHERE owner = %s
			and workflow_state in ("Approved")""", (str(user)), as_dict = 1)
	if get_form_list:
		if len(get_form_list) > 0:
			has_approved_form = "True"

	return has_approved_form
	
@frappe.whitelist(allow_guest=True)
def is_form_rejected(frm_name):
	has_rejected = "False"
	get_form_list = frappe.db.sql("""SELECT workflow_state FROM `tabEligibility Form` WHERE name = %s""", (str(frm_name)), as_dict = 1)
	if get_form_list:
		if len(get_form_list) > 0:
			has_rejected = "True" if get_form_list[0]['workflow_state'] == 'Rejected' else "False"

	return has_rejected

@frappe.whitelist(allow_guest=True)
def get_sample_image():
	image_path = frappe.db.get_value("Unlimited Settings", None, "sample_image")
	return image_path
