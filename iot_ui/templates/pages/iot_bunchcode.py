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
from cloud.cloud.doctype.cloud_company_group.cloud_company_group import list_user_groups as _list_user_groups
from cloud.cloud.doctype.cloud_company.cloud_company import list_user_companies

def list_curuser_groups():
	curuser = frappe.session.user
	groups = _list_user_groups(curuser)
	for g in groups:
		g.group_name = frappe.get_value("Cloud Company Group", g.name, "group_name")
	return groups

def get_bunch_codes(group, start=0, search=None):
	filters = {
		"owner_type": "Cloud Company Group",
		"owner_id": group
	}
	if search:
		filters["bunch_name"] = ("like", "%{0}%".format(search))
	bunch_codes = frappe.get_all("IOT Device Bunch", filters=filters,
		limit_start=start, limit_page_length=10)
	return bunch_codes

def get_context(context):
	if frappe.session.user == 'Guest':
		frappe.local.flags.redirect_location = "/login"
		raise frappe.Redirect
	context.no_cache = 1
	context.show_sidebar = True
	context.no_cache = 1

	curuser = frappe.session.user
	context.language = frappe.db.get_value("User", frappe.session.user, ["language"])
	bunch_codes = []
	groups = list_curuser_groups()
	print("groups", groups)
	for g in groups:
		bunch_code = get_bunch_codes(g["name"], start=0)
		if bunch_code:
			#print(bunch_code)
			groupdesc = frappe.get_value("Cloud Company Group", g.name, "group_name")
			bunch_codes.append({"name": g["name"], "desc": groupdesc, "code": bunch_code})
		else:
			groupdesc = frappe.get_value("Cloud Company Group", g.name, "group_name")
			bunch_codes.append({"name": g["name"], "desc": groupdesc, "code": ""})
		pass
	print("sadasd", bunch_codes)
	context.group_bunch_codes = bunch_codes

	private_bunch_codes = frappe.get_all("IOT Device Bunch", filters={
		"owner_type": "User",
		"owner_id": frappe.session.user
	})
	if private_bunch_codes:
		context.private_bunch_codes = private_bunch_codes

	if 'Company Admin' in frappe.get_roles(frappe.session.user):
		context.isCompanyAdmin = True
	if 'App User' in frappe.get_roles(frappe.session.user):
		context.isAppUser = True

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
	context.title = _('iot_bunchcode')
	context.csrf_token = frappe.local.session.data.csrf_token
