#!/usr/bin/python
# -*- coding: UTF-8 -*-
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
import redis
import datetime, time
from frappe.utils import now, get_datetime, convert_utc_to_user_timezone, now_datetime

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
	context.title = _('iot_management')
	context.csrf_token = frappe.local.session.data.csrf_token

	device = frappe.get_doc('IOT Device', name)
	device.has_permission('read')
	context.doc = device
	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/12")
	context.iot_version = eval(client.hget(name, "version/value"))[1]
	# print("@@@@@@@@@@@@@@@@",context.iot_version)
	context.skynet_version = eval(client.hget(name, "skynet_version/value"))[1]
	_starttime = eval(client.hget(name, "starttime/value"))[1]
	context.uptime = int(eval(client.hget(name, "uptime/value"))[1]/1000)
	context.starttime = str(convert_utc_to_user_timezone(datetime.datetime.utcfromtimestamp(int(_starttime))).replace(tzinfo=None))