# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import json
import uuid
from frappe import _dict, throw, _

from iot.iot.doctype.iot_device.iot_device import IOTDevice
from cloud.cloud.doctype.cloud_company_group.cloud_company_group import list_user_groups as _list_user_groups
from cloud.cloud.doctype.cloud_company.cloud_company import list_user_companies
from iot.hdb_api import list_iot_devices
import redis
from iot.iot.doctype.iot_hdb_settings.iot_hdb_settings import IOTHDBSettings
from iot.hdb import iot_device_tree
from cloud.cloud.doctype.cloud_company_group.cloud_company_group import list_user_groups as _list_user_groups
from cloud.cloud.doctype.cloud_company.cloud_company import list_user_companies
from cloud.cloud.doctype.cloud_company.cloud_company import list_admin_companies
from cloud.cloud.doctype.cloud_company.cloud_company import list_users, get_domain
from cloud.cloud.doctype.cloud_employee.cloud_employee import add_employee


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

@frappe.whitelist()
def list_curuser_groups():
	curuser = frappe.session.user
	groups = _list_user_groups(curuser)
	for g in groups:
		g.group_name = frappe.get_value("Cloud Company Group", g.name, "group_name")
	print(groups)
	return groups

@frappe.whitelist()
def list_curuser_bunch_codes():
	bunch_codes = {}
	bunch_codes["group"] = {}
	groups = list_curuser_groups()
	for g in groups:
		bunch_code = get_bunch_codes(g["name"], start=0)
		if bunch_code:
			print(bunch_code)
			bunch_codes["group"][g["name"]] = bunch_code
		pass

	pri_bunch_codes = frappe.get_all("IOT Device Bunch", filters={
		"owner_type": "User",
		"owner_id": frappe.session.user
	})
	if pri_bunch_codes:
		bunch_codes["own"] = pri_bunch_codes

	if 'Company Admin' in frappe.get_roles(frappe.session.user):
		bunch_codes["isgroupadmin"] = True
	return bunch_codes


@frappe.whitelist()
def add_own_bunch_code():
	if 'IOT User' not in frappe.get_roles(frappe.session.user):
		frappe.throw(_("You are not an IOT User"))

	bunch_code = str(uuid.uuid1())
	print("***********", bunch_code)
	if frappe.get_value("IOT Device Bunch", {"code": bunch_code}):
		frappe.throw(_("Bunch code already exists!"))
	doc = frappe.get_doc({
		"doctype": "IOT Device Bunch",
		"bunch_name": bunch_code,
		"code": bunch_code,
		"owner_type": "User",
		"owner_id": frappe.session.user,
	}).insert()
	return {"code": bunch_code, "owner_id": frappe.session.user, "result": 'sucessful'}

@frappe.whitelist()
def del_bunch_code(bunch_code):
	ot = frappe.get_value("IOT Device Bunch", bunch_code, "owner_type")
	print("owner_type", ot)
	if ot == "Cloud Company Group":
		if 'Company Admin' in frappe.get_roles(frappe.session.user):
			try:
				frappe.delete_doc('IOT Device Bunch', bunch_code)
				return {"code": bunch_code, "result": 'sucessful'}
			except Exception as ex:
				return {"result": False, "reason": ex.message}
			pass
		else:
			return {"code": bunch_code, "result": 'failed', "reason": "not your bunchcode"}
	elif ot == "User":
		try:
			frappe.delete_doc('IOT Device Bunch',  bunch_code)
			return {"code": bunch_code, "result": 'sucessful'}
		except Exception as ex:
			return {"result": False, "reason": ex.message}

@frappe.whitelist()
def add_group_bunch_code(groupid):
	if 'Company Admin' in frappe.get_roles(frappe.session.user):
		pass
	if 'IOT User' not in frappe.get_roles(frappe.session.user):
		return {"result": 'failed', "reason": "You are not an IOT User"}
	bunch_code = str(uuid.uuid1())
	print("***********", bunch_code)
	if frappe.get_value("IOT Device Bunch", {"code": bunch_code}):
		return {"result": 'failed', "reason": "Bunch code already exists!"}
	doc = frappe.get_doc({
		"doctype": "IOT Device Bunch",
		"bunch_name": bunch_code,
		"code": bunch_code,
		"owner_type": "Cloud Company Group",
		"owner_id": groupid,
	}).insert()
	return {"code": bunch_code, "owner_id": groupid, "result": 'sucessful'}

def list_users_by_domain(domain):
	return frappe.get_all("User",
		filters={"email": ("like", "%@{0}".format(domain))},
		fields=["name", "full_name", "enabled", "email", "creation"])

@frappe.whitelist()
def list_possible_users(company):
	domain = get_domain(company)
	users = list_users_by_domain(domain)
	employees = list_users(company)
	return [user for user in users if user.name not in employees]

@frappe.whitelist()
def list_company_member(company):
	if 'Company Admin' not in frappe.get_roles(frappe.session.user):
		return False
	if frappe.db.get_value("Cloud Company", company, "enabled") != 1:
		return False
	return [d[0] for d in frappe.db.get_values("Cloud Employee", {"company": company})]

@frappe.whitelist()
def add_company_member(company, memberid):
	if 'Company Admin' in frappe.get_roles(frappe.session.user):
		comp = frappe.get_value("Cloud Employee", {"user": memberid}, "company")
		if comp:
			if comp != company:
				throw(_("User in in another company {0}").format(comp))
			return True

		if not frappe.get_value("Cloud Company", {"name": company, "admin": frappe.session.user}):
			throw(_("You not the admin of company {0}").format(company))

		doc = frappe.get_doc({"doctype": "Cloud Employee", "user": memberid, "company": company})
		doc.insert(ignore_permissions=True)
		frappe.db.commit()

		return _("Employee has ben added")

@frappe.whitelist()
def del_company_member(company, memberid):
	if 'Company Admin' in frappe.get_roles(frappe.session.user):
		if not frappe.get_value("Cloud Company", {"name": company, "admin": frappe.session.user}):
			throw(_("You not the admin of company {0}").format(company))

		frappe.delete_doc("Cloud Employee", memberid, ignore_permissions=True)
		return _("Employee has been deleted")

@frappe.whitelist()
def list_company_group(company):
	if 'Company Admin' not in frappe.get_roles(frappe.session.user):
		return False
	return [d[0] for d in frappe.db.get_values("Cloud Company Group", {"company": company})]

@frappe.whitelist()
def add_company_group(company):
	if 'Company Admin' in frappe.get_roles(frappe.session.user):
		pass

@frappe.whitelist()
def del_company_group(company, groupsid):
	if 'Company Admin' in frappe.get_roles(frappe.session.user):
		pass

@frappe.whitelist()
def list_group_member(groupid):
	if 'Company Admin' not in frappe.get_roles(frappe.session.user):
		pass
	users = []
	for d in frappe.db.get_values("Cloud Company GroupUser", {"parent": groupid}, ["user", "role", "modified", "creation"]):
		users.append(_dict({"name": d[0], "role": d[1], "modified": d[2], "creation": d[3], "group": groupid}))
	return users

@frappe.whitelist()
def list_member_group(user):
	groups = []
	appended_groups = []
	for d in frappe.db.get_values("Cloud Company GroupUser", {"user": user}, ["parent", "role", "modified", "creation"]):
		if frappe.get_value("Cloud Company Group", d[0], "enabled"):
			groups.append(_dict({"name": d[0], "role": d[1], "modified": d[2], "creation": d[3], "user": user}))
			appended_groups.append(d[0])
	for comp in list_admin_companies(user):
		for d in frappe.db.get_values("Cloud Company Group", {"company": comp, "enabled": 1}, "name"):
			if d[0] not in appended_groups:
				groups.append(_dict({"name": d[0], "role": "Admin", "user": user}))
	return groups

@frappe.whitelist()
def bind_member_group(company, membersid, groupsid):
	if 'Company Admin' in frappe.get_roles(frappe.session.user):
		pass

@frappe.whitelist()
def unbind_member_group(company, membersid, groupsid):
	if 'Company Admin' in frappe.get_roles(frappe.session.user):
		pass

@frappe.whitelist(allow_guest=True)
def ping():
	form_data = frappe.form_dict
	if frappe.request and frappe.request.method == "POST":
		if form_data.data:
			form_data = json.loads(form_data.data)
		return form_data.get("text") or "No Text"
	return 'pong'