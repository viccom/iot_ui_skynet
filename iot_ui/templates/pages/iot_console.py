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



UTC_FORMAT1 = "%Y-%m-%dT%H:%M:%S.%fZ"
UTC_FORMAT2 = "%Y-%m-%dT%H:%M:%SZ"


def utc2local(utc_st):
	now_stamp = time.time()
	local_time = datetime.datetime.fromtimestamp(now_stamp)
	utc_time = datetime.datetime.utcfromtimestamp(now_stamp)
	offset = local_time - utc_time
	local_st = utc_st + offset
	return local_st

def get_context(context):
	if frappe.session.user == 'Guest':
		frappe.local.flags.redirect_location = "/login"
		raise frappe.Redirect
	context.no_cache = 1
	context.show_sidebar = True
	context.csrf_token = frappe.local.session.data.csrf_token
	if 'Company Admin' in frappe.get_roles(frappe.session.user):
		context.isCompanyAdmin = True
	context.language = frappe.local.lang #frappe.db.get_value("User",frappe.session.user, ["language"])
	curuser = frappe.session.user
	context.userprofile = get_all(curuser)
	devices = list_iot_devices(curuser)
	userdevices_total = []
	userdevices_online = []
	userdevices_offline = []
	userdevices_offline_7d = []
	if devices["company_devices"]:
		for devs in devices["company_devices"]:
			for d in devs["devices"]:
				for dsn in d["sn"]:
					devinfo = IOTDevice.get_device_doc(dsn)
					#print(dir(devinfo))

					lasttime = get_datetime(devinfo.last_updated)
					nowtime = now_datetime()

					userdevices_total.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name, "device_desc": devinfo.description, "device_status": devinfo.device_status,  "last_updated": devinfo.last_updated, "device_company": devinfo.company,  "longitude": devinfo.longitude, "latitude": devinfo.latitude})
					if devinfo.device_status == "ONLINE":
						userdevices_online.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name, "device_desc": devinfo.description, "device_status": devinfo.device_status,  "last_updated": devinfo.last_updated, "device_company": devinfo.company,  "longitude": devinfo.longitude, "latitude": devinfo.latitude})
					elif devinfo.device_status == "OFFLINE" and (nowtime-lasttime).days >= 7:
						userdevices_offline_7d.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name,
						                           "device_desc": devinfo.description,
						                           "device_status": devinfo.device_status,
						                           "last_updated": devinfo.last_updated,
						                           "device_company": devinfo.company, "longitude": devinfo.longitude,
						                           "latitude": devinfo.latitude})
						userdevices_offline.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name, "device_desc": devinfo.description, "device_status": devinfo.device_status,  "last_updated": devinfo.last_updated, "device_company": devinfo.company,  "longitude": devinfo.longitude, "latitude": devinfo.latitude})

					else:
						userdevices_offline.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name, "device_desc": devinfo.description, "device_status": devinfo.device_status,  "last_updated": devinfo.last_updated, "device_company": devinfo.company,  "longitude": devinfo.longitude, "latitude": devinfo.latitude})
				pass
			pass
		pass

	if devices["shared_devices"]:
		for devs in devices["shared_devices"]:
			for d in devs["devices"]:
				for dsn in d["sn"]:
					devinfo = IOTDevice.get_device_doc(dsn)
					#print(dir(devinfo))
					userdevices_total.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name, "device_desc": devinfo.description, "device_status": devinfo.device_status,  "last_updated": devinfo.last_updated, "device_company": devinfo.company, "longitude": devinfo.longitude, "latitude": devinfo.latitude})
					if devinfo.device_status == "ONLINE":
						userdevices_online.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name, "device_desc": devinfo.description, "device_status": devinfo.device_status,  "last_updated": devinfo.last_updated, "device_company": devinfo.company,  "longitude": devinfo.longitude, "latitude": devinfo.latitude})
					elif devinfo.device_status == "OFFLINE" and (nowtime-lasttime).days >= 7:
						userdevices_offline_7d.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name,
						                           "device_desc": devinfo.description,
						                           "device_status": devinfo.device_status,
						                           "last_updated": devinfo.last_updated,
						                           "device_company": devinfo.company, "longitude": devinfo.longitude,
						                           "latitude": devinfo.latitude})
						userdevices_offline.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name, "device_desc": devinfo.description, "device_status": devinfo.device_status,  "last_updated": devinfo.last_updated, "device_company": devinfo.company,  "longitude": devinfo.longitude, "latitude": devinfo.latitude})

					else:
						userdevices_offline.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name, "device_desc": devinfo.description, "device_status": devinfo.device_status,  "last_updated": devinfo.last_updated, "device_company": devinfo.company,  "longitude": devinfo.longitude, "latitude": devinfo.latitude})

				pass
			pass
		pass

	if devices["private_devices"]:
		for d in devices["private_devices"]:
			for dsn in d["sn"]:
				devinfo = IOTDevice.get_device_doc(dsn)
				userdevices_total.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name, "device_desc": devinfo.description, "device_status": devinfo.device_status, "last_updated": devinfo.last_updated,  "device_company": curuser, "longitude": devinfo.longitude, "latitude": devinfo.latitude})
				if devinfo.device_status == "ONLINE":
					userdevices_online.append(
						{"device_name": devinfo.dev_name, "device_sn": devinfo.name, "device_desc": devinfo.description,
						 "device_status": devinfo.device_status, "last_updated": devinfo.last_updated,
						 "device_company": devinfo.company, "longitude": devinfo.longitude,
						 "latitude": devinfo.latitude})
				elif devinfo.device_status == "OFFLINE" and (nowtime - lasttime).days >= 7:
					userdevices_offline_7d.append(
						{"device_name": devinfo.dev_name, "device_sn": devinfo.name, "device_desc": devinfo.description,
						 "device_status": devinfo.device_status, "last_updated": devinfo.last_updated,
						 "device_company": devinfo.company, "longitude": devinfo.longitude,
						 "latitude": devinfo.latitude})
					userdevices_offline.append(
						{"device_name": devinfo.dev_name, "device_sn": devinfo.name, "device_desc": devinfo.description,
						 "device_status": devinfo.device_status, "last_updated": devinfo.last_updated,
						 "device_company": devinfo.company, "longitude": devinfo.longitude,
						 "latitude": devinfo.latitude})
				else:
					userdevices_offline.append(
						{"device_name": devinfo.dev_name, "device_sn": devinfo.name, "device_desc": devinfo.description,
						 "device_status": devinfo.device_status, "last_updated": devinfo.last_updated,
						 "device_company": devinfo.company, "longitude": devinfo.longitude,
						 "latitude": devinfo.latitude})
			pass
		pass
	context.userdevices = {"total":[0], "online":[0], "offline":[0], "offline_7d":[0]}

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
	print(n_list)
	context.leftnavlist = n_list
	context.title = 'iot_console'
