# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _
import redis
from iot.iot.doctype.iot_device.iot_device import IOTDevice
from cloud.cloud.doctype.cloud_company_group.cloud_company_group import list_user_groups as _list_user_groups
from cloud.cloud.doctype.cloud_company.cloud_company import list_user_companies
from iot.hdb_api import list_iot_devices
from iot.hdb import iot_device_tree, iot_device_cfg
from iot.iot.doctype.iot_hdb_settings.iot_hdb_settings import IOTHDBSettings
from iot.hdb import iot_device_tree


def get_context(context):
	name = frappe.form_dict.device or frappe.form_dict.name
	if not name:
		frappe.local.flags.redirect_location = "/"
		raise frappe.Redirect

	user_roles = frappe.get_roles(frappe.session.user)
	context.language = frappe.db.get_value("User", frappe.session.user, ["language"])
	if 'IOT User' not in user_roles or frappe.session.user == 'Guest':
		raise frappe.PermissionError
	context.no_cache = 1
	context.show_sidebar = True
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
	context.title = _('Devices_List')
	context.csrf_token = frappe.local.session.data.csrf_token

	device = frappe.get_doc('IOT Device', name)
	device.has_permission('read')
	context.doc = device

	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/11")
	context.devices = []
	for d in client.lrange(name, 0, -1):
		dev = {
			'sn': d
		}
		if d.encode("ascii") != name.encode("ascii"):
			if d[0:len(name)] == name:
				dev['name']= d[len(name):]
			context.devices.append(dev)
	if device.sn:
		context.vsn = iot_device_tree(device.sn)
	else:
		context.vsn = []