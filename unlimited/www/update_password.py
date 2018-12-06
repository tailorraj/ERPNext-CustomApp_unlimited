# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt
from __future__ import unicode_literals
from frappe.utils import cint
from frappe import _
import frappe
from frappe.utils.password import update_password as _update_password
from frappe.desk.form.load import get_docinfo

no_sitemap = 1
no_cache = 1

def get_context(context):
	context.no_breadcrumbs = True
	context.parents = [{"name":"me", "title":_("My Account")}]

class DuplicateToDoErrorAI(frappe.ValidationError): pass

def get(args=None):
	"""get assigned to"""
	if not args:
		args = frappe.local.form_dict

	get_docinfo(frappe.get_doc(args.get("doctype"), args.get("name")))

	return frappe.db.sql("""select owner, description from `tabToDo`
		where reference_type=%(doctype)s and reference_name=%(name)s and status="Open"
		order by modified desc limit 5""", args, as_dict=True)

def notify_assignment(assigned_by, owner, doc_type, doc_name, action='CLOSE',
	description=None, notify=0):
	"""
		Notify assignee that there is a change in assignment
	"""
	if not (assigned_by and owner and doc_type and doc_name): return

	# self assignment / closing - no message
	if assigned_by==owner:
		return

	from frappe.boot import get_fullnames
	user_info = get_fullnames()

	# Search for email address in description -- i.e. assignee
	from frappe.utils import get_link_to_form
	assignment = get_link_to_form(doc_type, doc_name, label="%s: %s" % (doc_type, doc_name))
	owner_name = user_info.get(owner, {}).get('fullname')
	user_name = user_info.get(frappe.session.get('user'), {}).get('fullname')
	if action=='CLOSE':
		if owner == frappe.session.get('user'):
			arg = {
				'contact': assigned_by,
				'txt': _("The task {0}, that you assigned to {1}, has been closed.").format(assignment,
						owner_name)
			}
		else:
			arg = {
				'contact': assigned_by,
				'txt': _("The task {0}, that you assigned to {1}, has been closed by {2}.").format(assignment,
					owner_name, user_name)
			}
	else:
		description_html = "<p>{0}</p>".format(description)
		arg = {
			'contact': owner,
			'txt': _("A new task, {0}, has been assigned to you by {1}. {2}").format(assignment,
				user_name, description_html),
			'notify': notify
		}

	arg["parenttype"] = "Assignment"

	from frappe.desk.page.chat import chat
	chat.post(**arg)

def add_assign(args=None):
	"""add in someone's to do list
		args = {
			"assign_to": ,
			"doctype": ,
			"name": ,
			"description":
		}

	"""
	if not args:
		args = frappe.local.form_dict

	if frappe.db.sql("""select owner from `tabToDo`
		where reference_type=%(doctype)s and reference_name=%(name)s and status="Open"
		and owner=%(assign_to)s""", args):
		frappe.throw(_("Already in user's To Do list"), DuplicateToDoErrorAI)

	else:
		from frappe.utils import nowdate

		# if args.get("re_assign"):
		# 	remove_from_todo_if_already_assigned(args['doctype'], args['name'])

		d = frappe.get_doc({
			"doctype":"ToDo",
			"owner": args['assign_to'],
			"reference_type": args['doctype'],
			"reference_name": args['name'],
			"description": args.get('description'),
			"priority": args.get("priority", "Medium"),
			"status": "Open",
			"date": args.get('date', nowdate()),
			"assigned_by": args.get('assigned_by', frappe.session.user),
		}).insert(ignore_permissions=True)

		# set assigned_to if field exists
		if frappe.get_meta(args['doctype']).get_field("assigned_to"):
			frappe.db.set_value(args['doctype'], args['name'], "assigned_to", args['assign_to'])

		doc = frappe.get_doc(args['doctype'], args['name'])

		# if assignee does not have permissions, share
		# if not frappe.has_permission(doc=doc, user=args['assign_to']):
		# 	frappe.share.add(doc.doctype, doc.name, args['assign_to'])
		# 	frappe.msgprint(_('Shared with user {0} with read access').format(args['assign_to']), alert=True)

	# notify
	notify_assignment(d.assigned_by, d.owner, d.reference_type, d.reference_name, action='ASSIGN',\
			 description=args.get("description"), notify=args.get('notify'))

	return get(args)

def reset_user_data(user):
	user_doc = frappe.get_doc("User", user)
	redirect_url = user_doc.redirect_url
	user_doc.reset_password_key = ''
	user_doc.redirect_url = ''
	user_doc.save(ignore_permissions=True)

	return user_doc, redirect_url

def _get_user_for_update_password(key, old_password):
	# verify old password
	if key:
		user = frappe.db.get_value("User", {"reset_password_key": key})
		if not user:
			return {
				'message': _("Cannot Update: Incorrect / Expired Link.")
			}

	elif old_password:
		# verify old password
		frappe.local.login_manager.check_password(frappe.session.user, old_password)
		user = frappe.session.user

	else:
		return

	return {
		'user': user
	}

def handle_password_test_fail(result):
	suggestions = result['feedback']['suggestions'][0] if result['feedback']['suggestions'] else ''
	warning = result['feedback']['warning'] if 'warning' in result['feedback'] else ''
	suggestions += "<br>" + _("Hint: Include symbols, numbers and capital letters in the password") + '<br>'
	frappe.throw(_('Invalid Password: ' + ' '.join([warning, suggestions])))

@frappe.whitelist(allow_guest=True)
def test_password_strength(new_password, key=None, old_password=None, user_data=[]):
	from frappe.utils.password_strength import test_password_strength as _test_password_strength

	password_policy = frappe.db.get_value("System Settings", None,
		["enable_password_policy", "minimum_password_score"], as_dict=True) or {}

	enable_password_policy = cint(password_policy.get("enable_password_policy", 0))
	minimum_password_score = cint(password_policy.get("minimum_password_score", 0))

	if not enable_password_policy:
		return {}

	if not user_data:
		user_data = frappe.db.get_value('User', frappe.session.user,
			['first_name', 'middle_name', 'last_name', 'email', 'birth_date'])

	if new_password:
		result = _test_password_strength(new_password, user_inputs=user_data)
		password_policy_validation_passed = False

		# score should be greater than 0 and minimum_password_score
		if result.get('score') and result.get('score') >= minimum_password_score:
			password_policy_validation_passed = True

		result['feedback']['password_policy_validation_passed'] = password_policy_validation_passed
		return result

@frappe.whitelist(allow_guest=True)
def update_password(new_password, key=None, old_password=None):
	result = test_password_strength(new_password, key, old_password)
	feedback = result.get("feedback", None)

	if feedback and not feedback.get('password_policy_validation_passed', False):
		handle_password_test_fail(result)

	res = _get_user_for_update_password(key, old_password)
	if res.get('message'):
		return res['message']
	else:
		user = res['user']

	_update_password(user, new_password)

	#get default sales person to whome the lead will be assign.
	default_sales_person = frappe.db.get_value("Unlimited Settings", None, "default_sales_person")
	employee = frappe.db.get_value("Sales Person", default_sales_person, "employee")
	person_user_id = frappe.db.get_value("Employee", employee, "user_id")
	chek_if_user_lead_available = frappe.db.get_value("Lead", {"email_id":str(user)}, "name")

	if key and new_password and not chek_if_user_lead_available:
		#create a lead while setting up the password.
		lead = frappe.get_doc({
				"doctype":"Lead",
				"lead_name": frappe.db.get_value("User", {"email":str(user)}, "first_name"),
				"email_id": str(user),
				"phone": frappe.db.get_value("User", {"email":str(user)}, "phone"),
				"lead_owner": str(person_user_id)
			})
		lead.flags.ignore_permissions = True
		lead.insert()

		#assign created lead to the default sales person.
		from frappe.utils import nowdate
		args = {
				"assign_to": str(person_user_id),
				"description": lead.lead_name,
				"date": nowdate(),
				"notify": 1,
				"priority": "High",
				"doctype": "Lead",
				"name": lead.name,
				# "assigned_by": "Administrator"
			}
		add_assign(args)

	user_doc, redirect_url = reset_user_data(user)
	# frappe.msgprint(str(redirect_url))
	# frappe.throw(str(user_doc))

	# get redirect url from cache
	redirect_to = frappe.cache().hget('redirect_after_login', user)
	if redirect_to:
		redirect_url = redirect_to
		frappe.cache().hdel('redirect_after_login', user)

	frappe.local.login_manager.login_as(user)

	# frappe.msgprint(str(user_doc.user_type))
	# frappe.throw(str(redirect_url) + " ---Hello")

	if user_doc.user_type == "System User":
		return "/desk"
	else:
		# frappe.throw("Hello 1")
		return redirect_url if redirect_url else "/"
