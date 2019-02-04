from __future__ import unicode_literals

import frappe

def get_context(context):
	# do your magic here
	pass

def get_list_context(context):
	# frappe.throw("Hello")
	context.row_template = "unlimited/templates/includes/tenant_order/tenant_order_list_row.html"
	context.get_list = get_tenant_order_list

def get_tenant_order_list(doctype, txt, filters, limit_start, limit_page_length = 20, order_by='modified desc'):
	tenant_orders = frappe.get_all("Tenant Order", filters={
	"owner": frappe.session.user	
	}, fields=["*"], limit_page_length=10, order_by="creation desc")
	return tenant_orders
