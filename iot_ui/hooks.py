# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "iot_ui"
app_title = "Iot Ui"
app_publisher = "viccom"
app_description = "Iot Ui"
app_icon = "octicon octicon-versions"
app_color = "olive"
app_email = "viccom.dong@symid.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/iot_ui/css/iot_ui.css"
# app_include_js = "/assets/iot_ui/js/iot_ui.js"

# include js, css files in header of web template
# web_include_css = "/assets/iot_ui/css/iot_ui.css"
# web_include_js = "/assets/iot_ui/js/iot_ui.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "iot_ui.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "iot_ui.install.before_install"
# after_install = "iot_ui.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "iot_ui.notifications.get_notification_config"

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
# 		"iot_ui.tasks.all"
# 	],
# 	"daily": [
# 		"iot_ui.tasks.daily"
# 	],
# 	"hourly": [
# 		"iot_ui.tasks.hourly"
# 	],
# 	"weekly": [
# 		"iot_ui.tasks.weekly"
# 	]
# 	"monthly": [
# 		"iot_ui.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "iot_ui.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "iot_ui.event.get_events"
# }
website_route_rules = [
	{"from_route": "/iot_devinfo/<path:name>", "to_route": "iot_devinfo"},
	{"from_route": "/iot_management/<path:name>", "to_route": "iot_management"},
]
