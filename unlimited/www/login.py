# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
import frappe.utils
from frappe.utils.oauth import get_oauth2_authorize_url, get_oauth_keys, login_via_oauth2, login_oauth_user as _login_oauth_user, redirect_post_login
import json
from frappe import _
from frappe.auth import LoginManager
from frappe.integrations.doctype.ldap_settings.ldap_settings import get_ldap_settings
from frappe.website.utils import is_signup_enabled

no_cache = True

def get_context(context):
	if frappe.session.user != "Guest" and frappe.session.data.user_type=="System User":
		frappe.local.flags.redirect_location = "/desk"
		raise frappe.Redirect

	# get settings from site config
	context.no_header = True
	context.for_test = 'login.html'
	context["title"] = "Login"
	context["disable_signup"] = frappe.utils.cint(frappe.db.get_value("Website Settings", "Website Settings", "disable_signup"))

	for provider in ("google", "github", "facebook", "frappe"):
		if get_oauth_keys(provider):
			context["{provider}_login".format(provider=provider)] = get_oauth2_authorize_url(provider)
			context["social_login"] = True

	ldap_settings = get_ldap_settings()
	context["ldap_settings"] = ldap_settings

	login_name_placeholder = [_("Email address")]

	if frappe.utils.cint(frappe.get_system_settings("allow_login_using_mobile_number")):
		login_name_placeholder.append(_("Mobile number"))

	if frappe.utils.cint(frappe.get_system_settings("allow_login_using_user_name")):
		login_name_placeholder.append(_("Username"))

	context['login_name_placeholder'] = ' {0} '.format(_('or')).join(login_name_placeholder)

	return context

@frappe.whitelist(allow_guest=True)
def login_via_google(code, state):
	login_via_oauth2("google", code, state, decoder=json.loads)

@frappe.whitelist(allow_guest=True)
def login_via_github(code, state):
	login_via_oauth2("github", code, state)

@frappe.whitelist(allow_guest=True)
def login_via_facebook(code, state):
	login_via_oauth2("facebook", code, state, decoder=json.loads)

@frappe.whitelist(allow_guest=True)
def login_via_frappe(code, state):
	login_via_oauth2("frappe", code, state, decoder=json.loads)

@frappe.whitelist(allow_guest=True)
def login_oauth_user(data=None, provider=None, state=None, email_id=None, key=None, generate_login_token=False):
	if not ((data and provider and state) or (email_id and key)):
		frappe.respond_as_web_page(_("Invalid Request"), _("Missing parameters for login"), http_status_code=417)
		return

	_login_oauth_user(data, provider, state, email_id, key, generate_login_token)

@frappe.whitelist(allow_guest=True)
def login_via_token(login_token):
	sid = frappe.cache().get_value("login_token:{0}".format(login_token), expires=True)
	if not sid:
		frappe.respond_as_web_page(_("Invalid Request"), _("Invalid Login Token"), http_status_code=417)
		return

	frappe.local.form_dict.sid = sid
	frappe.local.login_manager = LoginManager()

	redirect_post_login(desk_user = frappe.db.get_value("User", frappe.session.user, "user_type")=="System User")

@frappe.whitelist(allow_guest=True)
def sign_up(email, full_name, dob, phone_number, address, guardian_name, redirect_to):
	
	if not is_signup_enabled():
		frappe.throw(_('Sign Up is disabled'), title='Not Allowed')

	user = frappe.db.get("User", {"email": email})
	if user:
		if user.disabled:
			return 0, _("Registered but disabled")
		else:
			return 0, _("Already Registered")
	else:
		if frappe.db.sql("""select count(*) from tabUser where
			HOUR(TIMEDIFF(CURRENT_TIMESTAMP, TIMESTAMP(modified)))=1""")[0][0] > 300:

			frappe.respond_as_web_page(_('Temperorily Disabled'),
				_('Too many users signed up recently, so the registration is disabled. Please try back in an hour'),
				http_status_code=429)	

		from frappe.utils import random_string
		import datetime

		date_format_dict = {"yyyy-mm-dd":"%Y-%m-%d","dd-mm-yyyy":"%d-%m-%Y","dd/mm/yyyy":"%d/%m/%Y","dd.mm.yyyy":"%d.%m.%Y","mm/dd/yyyy":"%m/%d/%Y","mm-dd-yyyy":"%m-%d-%Y"}

		get_date_format_string = date_format_dict["mm-dd-yyyy"]
		get_system_date_format = frappe.db.get_value("System Settings", None, "date_format")
		if get_system_date_format in date_format_dict:
			get_date_format_string = date_format_dict[str(get_system_date_format)]
		else:
			frappe.db.set_value("System Settings", None, "date_format", "mm-dd-yyyy")
			frappe.db.commit()

		datetime_obj = datetime.datetime.strptime(dob, '%Y-%m-%d').strftime(str(get_date_format_string))

		user = frappe.get_doc({
			"doctype":"User",
			"email": email,
			"first_name": full_name,
			"birth_date": frappe.utils.getdate(datetime_obj),
			"phone": phone_number,
			"address": address,
			"guardian_name": guardian_name,
			"enabled": 1,
			"new_password": random_string(10),
			"user_type": "Website User"
		})
		user.flags.ignore_permissions = True
		user.insert()


		# set default signup role as per Portal Settings
		default_role = frappe.db.get_value("Portal Settings", None, "default_role")
		if default_role:
			user.add_roles(default_role)
		# frappe.throw("--- "+ str(redirect_to) + " ---Hello")
		if redirect_to:
			frappe.cache().hset('redirect_after_login', user.name, redirect_to)

		if user.flags.email_sent:
			return 1, _("Please check your email for verification")
		else:
			return 2, _("Please ask your administrator to verify your sign-up")
