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
	if 'App User' in frappe.get_roles(frappe.session.user):
		context.isAppUser = True

	n_list = [{"url": "/iot_management/"+str(name), "name": "网关信息", "ico": "fa fa-lastfm-square", "id": "1"}, {"url": "/iot_applist/"+str(name), "name": "应用管理", "ico": "fa fa-ioxhost", "id": "2"}]

	n_list.sort(key=lambda k: (k.get('id', 0)))
	context.leftnavlist = n_list
	context.title = _('iot_applist')
	context.iotsn = name
	context.csrf_token = frappe.local.session.data.csrf_token
	context.user = frappe.session.user

