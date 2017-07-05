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
	if frappe.session.user == 'Guest':
		frappe.local.flags.redirect_location = "/login"
		raise frappe.Redirect
	context.no_cache = 1
	context.show_sidebar = True
	context.no_cache = 1

	# ent_devices = []
	curuser = frappe.session.user
	# groups = _list_user_groups(curuser)
	# print(groups)
	# companies = list_user_companies(curuser)
	# print(companies)
	# for g in groups:
	# 	bunch_codes = [d[0] for d in frappe.db.get_values("IOT Device Bunch", {
	# 		"owner_id": g.name,
	# 		"owner_type": "Cloud Company Group"
	# 	}, "code")]
	# 	print(bunch_codes)
	# 	sn_list = []
	# 	for c in bunch_codes:
	# 		sn_list.append({"bunch": c, "sn": IOTDevice.list_device_sn_by_bunch(c)})
	# 	ent_devices.append({"group": g.name, "devices": sn_list, "role": g.role})
	# print("ent_devices:", ent_devices)

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
	context.title = _('gateways_list')
