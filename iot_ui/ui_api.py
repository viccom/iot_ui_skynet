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
import redis
from iot.iot.doctype.iot_hdb_settings.iot_hdb_settings import IOTHDBSettings
from iot.hdb import iot_device_tree


@frappe.whitelist()
def devices_list_array():
	curuser = frappe.session.user
	devices = list_iot_devices(curuser)
	print(devices)
	userdevices = []
	if devices["company_devices"]:
		for devs in devices["company_devices"]:
			for d in devs["devices"]:
				for dsn in d["sn"]:
					devinfo = IOTDevice.get_device_doc(dsn)
					#print(devinfo.name, devinfo.dev_name, devinfo.description, devinfo.device_status, devinfo.company)
					userdevices.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name, "device_desc": devinfo.description, "device_status": devinfo.device_status, "device_company": devinfo.company})
				pass
			pass
		pass

	if devices["shared_devices"]:
		for devs in devices["shared_devices"]:
			for d in devs["devices"]:
				for dsn in d["sn"]:
					devinfo = IOTDevice.get_device_doc(dsn)
					#print(dir(devinfo))
					#print(devinfo.name, devinfo.dev_name, devinfo.description, devinfo.device_status, devinfo.company)
					userdevices.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name, "device_desc": devinfo.description, "device_status": devinfo.device_status, "device_company": devinfo.company})
				pass
			pass
		pass

	if devices["private_devices"]:
		for d in devices["private_devices"]:
			for dsn in d["sn"]:
				devinfo = IOTDevice.get_device_doc(dsn)
				#print(devinfo.name, devinfo.dev_name, devinfo.description, devinfo.device_status, devinfo.company)
				userdevices.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name, "device_desc": devinfo.description, "device_status": devinfo.device_status, "device_company": curuser})
			pass
		pass

	return userdevices

@frappe.whitelist()
def iot_devices_array(sn=None):
	sn = sn or frappe.form_dict.get('sn')
	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/1")
	devices = []
	for d in client.lrange(sn, 0, -1):
		dev = {
			'sn': d
		}
		if d[0:len(sn)] == sn:
			dev['name']= d[len(sn):]

		devices.append(dev)
	return devices

@frappe.whitelist(allow_guest=True)
def ping():
	form_data = frappe.form_dict
	if frappe.request and frappe.request.method == "POST":
		if form_data.data:
			form_data = json.loads(form_data.data)
		return form_data.get("text") or "No Text"
	return 'pong'