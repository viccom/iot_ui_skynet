# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _

from iot.iot.doctype.iot_device.iot_device import IOTDevice
from cloud.cloud.doctype.cloud_company_group.cloud_company_group import list_user_groups as _list_user_groups
from cloud.cloud.doctype.cloud_company.cloud_company import list_user_companies
from iot.hdb_api import list_iot_devices


def get_context(context):
	eventid = frappe.form_dict.eventid
	if not eventid:
		frappe.local.flags.redirect_location = "/"
		raise frappe.Redirect
	if frappe.session.user == 'Guest':
		frappe.local.flags.redirect_location = "/login"
		raise frappe.Redirect

	context.eventid = eventid
	event = frappe.get_doc("IOT Device Error", eventid)
	# print(event.error_info)
	context.device = event.device
	context.error_type = event.error_type
	context.error_key = event.error_key
	context.error_level = event.error_level
	context.error_info = event.error_info
	context.time = event.time

	query_ev = frappe.db.get_list("Error Visited", fields=["error_visited"], filters={"user": frappe.session.user, "error_visited": eventid})
	print(query_ev)
	if query_ev:
		hasread = 1
	else:
		hasread = 0
	context.hasread = hasread

	context.no_cache = 1
	context.show_sidebar = True

	context.language = frappe.db.get_value("User", frappe.session.user, ["language"])
	context.csrf_token = frappe.local.session.data.csrf_token

	if 'Company Admin' in frappe.get_roles(frappe.session.user):
		context.isCompanyAdmin = True

	menulist = frappe.get_all("Iot Menu")
	n_list = []
	for m in menulist:
		dd = {}
		dd['url'] = frappe.get_value("Iot Menu", m['name'], "menuurl")
		dd['name'] = frappe.get_value("Iot Menu", m['name'], "menuname")
		dd['ico'] = frappe.get_value("Iot Menu", m['name'], "menuico")
		dd['id'] = frappe.get_value("Iot Menu", m['name'], "ordernum")
		n_list.append(dd)

	n_list.sort(key=lambda k: (k.get('id', 0)))
	context.leftnavlist = n_list
	context.title = _('iot_event_info')
