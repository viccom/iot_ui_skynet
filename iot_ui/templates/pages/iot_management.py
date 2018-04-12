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
import requests
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
	if 'App User' in frappe.get_roles(frappe.session.user):
		context.isAppUser = True

	n_list = [{"url": "/iot_management/"+str(name), "name": "网关信息", "ico": "fa fa-lastfm-square", "id": "1"}, {"url": "/iot_applist/"+str(name), "name": "应用管理", "ico": "fa fa-ioxhost", "id": "2"}]

	n_list.sort(key=lambda k: (k.get('id', 0)))
	context.leftnavlist = n_list
	context.title = _('iot_management')
	context.csrf_token = frappe.local.session.data.csrf_token

	device = frappe.get_doc('IOT Device', name)
	device.has_permission('read')
	context.doc = device
	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/12")
	context.iot_version = None
	context.skynet_version = None
	context.iot_lastver = None
	context.skynet_lastver = None
	context.starttime = None
	context.uptime = None
	context.public_ip = None
	context.public_port = None
	context.applist = {}
	if client.exists(name):
		if client.hget(name, "version/value"):
			context.iot_version = eval(client.hget(name, "version/value"))[1]
		# print("@@@@@@@@@@@@@@@@",context.iot_version)
		if client.hget(name, "skynet_version/value"):
			context.skynet_version = eval(client.hget(name, "skynet_version/value"))[1]
		if client.hget(name, "starttime/value"):
			_starttime = eval(client.hget(name, "starttime/value"))[1]
			context.starttime = str(
				convert_utc_to_user_timezone(datetime.datetime.utcfromtimestamp(int(_starttime))).replace(tzinfo=None))
		if client.hget(name, "uptime/value"):
			context.uptime = int(eval(client.hget(name, "uptime/value"))[1] / 1000)
		if client.hget(name, "skynet_platform/value"):
			context.skynet_platform = eval(client.hget(name, "skynet_platform/value"))[1]
		filters = {"app": 'skynet_iot'}
		try:
			context.iot_lastver = frappe.db.get_all("IOT Application Version", "*", filters, order_by="version").pop().version
		except Exception as err:
			pass
		filters = {"app": 'amd_skynet'}
		try:
			context.skynet_lastver = frappe.db.get_all("IOT Application Version", "*", filters, order_by="version").pop().version
		except Exception as err:
			pass
		s = requests.Session()
		s.auth = ("api", "Pa88word")
		r = s.get('http://127.0.0.1:18083/api/v2/nodes/emq@127.0.0.1/clients/'+name)
		rdict = json.loads(r.text)
		context.public_ip = rdict['result']['objects'][0]['ipaddress']
		print(rdict)
		context.public_port = rdict['result']['objects'][0]['port']
		client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/6")
		context.applist = json.loads(client.get(name))

