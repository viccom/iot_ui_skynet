# coding=utf-8
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import json
import time
import datetime
from frappe import _
from frappe.utils.user import get_fullname_and_avatar
from iot.hdb_api import list_iot_devices
from iot.iot.doctype.iot_device.iot_device import IOTDevice
from frappe.utils import now, get_datetime, convert_utc_to_user_timezone, now_datetime
from iot_ui.ui_api import get_all
import frappe.share

def get_context(context):
	if frappe.session.user == 'Guest':
		frappe.local.flags.redirect_location = "/login"
		raise frappe.Redirect
	context.no_cache = 1
	context.show_sidebar = True
	context.csrf_token = frappe.local.session.data.csrf_token
	if 'Company Admin' in frappe.get_roles(frappe.session.user):
		context.isCompanyAdmin = True
	if 'App User' in frappe.get_roles(frappe.session.user):
		context.isAppUser = True

	context.language = frappe.local.lang #frappe.db.get_value("User",frappe.session.user, ["language"])
	curuser = frappe.session.user
	context.userprofile = get_all(curuser)
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
	context.title = 'iot_profile'
