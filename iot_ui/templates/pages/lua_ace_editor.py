# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import json
import time
import datetime
import commands, os
from frappe import _
from frappe.utils.user import get_fullname_and_avatar
from iot_ui.ui_api import list_iot_devices
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
	print("context.csrf_token----------------",context.csrf_token)
	if 'Company Admin' in frappe.get_roles(frappe.session.user):
		context.isCompanyAdmin = True
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

	verfile = "/home/frappe/frappe-bench/sites/assets/lua/apps/dev1/ver.ver"
	if os.path.exists(verfile):
		with open(verfile, 'r') as f:
			appver = json.loads(f.read())["ver"]
		# print(appver)
	context.appver = appver
	flist = os.listdir("/home/frappe/frappe-bench/sites/assets/lua/apps/dev1/")
	for f in flist:
		if "link" in f:
			context.luafile = f
			break
		else:
			context.luafile = "app.lua"
	context.leftnavlist = n_list
	context.title = 'lua_ace_editor'
