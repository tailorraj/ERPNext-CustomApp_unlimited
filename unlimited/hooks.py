# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version
from frappe import _

app_name = "unlimited"
app_title = "Unlimited Tomorrow"
app_publisher = "August Infotech"
app_description = "Customization"
app_icon = "octicon octicon-fold"
app_color = "#9e94a5"
app_email = "info@augustinfotech.com"
app_license = "info@augustinfotech.com"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/unlimited/css/unlimited.css"
# app_include_js = "/assets/unlimited/js/unlimited.js"

# include js, css files in header of web template
# web_include_css = "/assets/unlimited/css/unlimited.css"
# web_include_js = "/assets/unlimited/js/unlimited.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "unlimited.utils.get_home_page"

# Generators
# ----------

#fixtures = ["Web Form","Portal Settings","Workflow","Email Alert"]

fixtures = [
    {
        'doctype': 'Web Form',
        'filters': [['module', '=', 'Unlimited Tomorrow']],
    },
	"Portal Settings",
	"Workflow",
	"Email Alert"
]

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

#standard_portal_menu_items = [
#	{"title": _("Eligibility Form"), "route": "/eligibility-form", "reference_doctype": "Eligibility Form"}
#]

# Installation
# ------------

# before_install = "unlimited.install.before_install"
# after_install = "unlimited.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "unlimited.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"unlimited.tasks.all"
# 	],
# 	"daily": [
# 		"unlimited.tasks.daily"
# 	],
# 	"hourly": [
# 		"unlimited.tasks.hourly"
# 	],
# 	"weekly": [
# 		"unlimited.tasks.weekly"
# 	]
# 	"monthly": [
# 		"unlimited.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "unlimited.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "unlimited.event.get_events"
# }

