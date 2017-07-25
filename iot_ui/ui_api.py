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
from frappe.utils.user import get_user_fullname
from frappe.utils import now, get_datetime, convert_utc_to_user_timezone, now_datetime


def get_all(user):
	first_name, last_name, avatar, name, language, phone, mobile_no, last_login, last_ip = frappe.db.get_value("User",
		user, ["first_name", "last_name", "user_image", "name", "language", "phone", "mobile_no", "last_login", "last_ip"])
	return _dict({
		"fullname": " ".join(filter(None, [first_name, last_name])),
		"avatar": avatar,
		"name": name,
		"language": language,
		"phone": phone,
		"mobile_no": mobile_no,
		"last_login": last_login,
		"last_ip": last_ip
	})




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

def get_post_json_data():
	if frappe.request.method != "POST":
		throw(_("Request Method Must be POST!"))
	ctype = frappe.get_request_header("Content-Type")
	if "json" not in ctype.lower():
		throw(_("Incorrect HTTP Content-Type found {0}").format(ctype))
	if not frappe.form_dict.data:
		throw(_("JSON Data not found!"))
	return frappe._dict(json.loads(frappe.form_dict.data))

@frappe.whitelist()
def devices_list_array(filter):
	curuser = frappe.session.user
	devices = list_iot_devices(curuser)
	#print(devices)
	userdevices = []
	userdevices_online = []
	userdevices_offline = []
	userdevices_offline_7d = []
	if devices["company_devices"]:
		for devs in devices["company_devices"]:
			for d in devs["devices"]:
				for dsn in d["sn"]:
					devinfo = IOTDevice.get_device_doc(dsn)
					#print(dir(devinfo))
					#print(devinfo.name, devinfo.dev_name, devinfo.description, devinfo.device_status, devinfo.company)
					lasttime = get_datetime(devinfo.last_updated)
					nowtime = now_datetime()
					userdevices.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name, "device_desc": devinfo.description, "device_status": devinfo.device_status,  "last_updated": devinfo.last_updated, "device_company": devinfo.company,  "longitude": devinfo.longitude, "latitude": devinfo.latitude})
					if devinfo.device_status == "ONLINE":
						userdevices_online.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name,
						                           "device_desc": devinfo.description,
						                           "device_status": devinfo.device_status,
						                           "last_updated": devinfo.last_updated,
						                           "device_company": devinfo.company, "longitude": devinfo.longitude,
						                           "latitude": devinfo.latitude})
					elif devinfo.device_status == "OFFLINE" and (nowtime - lasttime).days >= 7:
						userdevices_offline_7d.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name,
						                               "device_desc": devinfo.description,
						                               "device_status": devinfo.device_status,
						                               "last_updated": devinfo.last_updated,
						                               "device_company": devinfo.company,
						                               "longitude": devinfo.longitude, "latitude": devinfo.latitude})
						userdevices_offline.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name,
						                            "device_desc": devinfo.description,
						                            "device_status": devinfo.device_status,
						                            "last_updated": devinfo.last_updated,
						                            "device_company": devinfo.company, "longitude": devinfo.longitude,
						                            "latitude": devinfo.latitude})
					else:
						userdevices_offline.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name,
						                            "device_desc": devinfo.description,
						                            "device_status": devinfo.device_status,
						                            "last_updated": devinfo.last_updated,
						                            "device_company": devinfo.company, "longitude": devinfo.longitude,
						                            "latitude": devinfo.latitude})
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
					lasttime = get_datetime(devinfo.last_updated)
					nowtime = now_datetime()
					userdevices.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name, "device_desc": devinfo.description, "device_status": devinfo.device_status,  "last_updated": devinfo.last_updated, "device_company": devinfo.company, "longitude": devinfo.longitude, "latitude": devinfo.latitude})
					if devinfo.device_status == "ONLINE":
						userdevices_online.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name,
						                           "device_desc": devinfo.description,
						                           "device_status": devinfo.device_status,
						                           "last_updated": devinfo.last_updated,
						                           "device_company": devinfo.company, "longitude": devinfo.longitude,
						                           "latitude": devinfo.latitude})
					elif devinfo.device_status == "OFFLINE" and (nowtime - lasttime).days >= 7:
						userdevices_offline_7d.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name,
						                               "device_desc": devinfo.description,
						                               "device_status": devinfo.device_status,
						                               "last_updated": devinfo.last_updated,
						                               "device_company": devinfo.company,
						                               "longitude": devinfo.longitude, "latitude": devinfo.latitude})
						userdevices_offline.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name,
						                            "device_desc": devinfo.description,
						                            "device_status": devinfo.device_status,
						                            "last_updated": devinfo.last_updated,
						                            "device_company": devinfo.company, "longitude": devinfo.longitude,
						                            "latitude": devinfo.latitude})
					else:
						userdevices_offline.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name,
						                            "device_desc": devinfo.description,
						                            "device_status": devinfo.device_status,
						                            "last_updated": devinfo.last_updated,
						                            "device_company": devinfo.company, "longitude": devinfo.longitude,
						                            "latitude": devinfo.latitude})

				pass
			pass
		pass

	if devices["private_devices"]:
		for d in devices["private_devices"]:
			for dsn in d["sn"]:
				devinfo = IOTDevice.get_device_doc(dsn)
				#print(dir(devinfo))
				#print(devinfo.name, devinfo.dev_name, devinfo.description, devinfo.device_status, devinfo.company)
				lasttime = get_datetime(devinfo.last_updated)
				nowtime = now_datetime()
				userdevices.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name, "device_desc": devinfo.description, "device_status": devinfo.device_status, "last_updated": devinfo.last_updated,  "device_company": curuser, "longitude": devinfo.longitude, "latitude": devinfo.latitude})
				if devinfo.device_status == "ONLINE":
					userdevices_online.append(
						{"device_name": devinfo.dev_name, "device_sn": devinfo.name, "device_desc": devinfo.description,
						 "device_status": devinfo.device_status, "last_updated": devinfo.last_updated,
						 "device_company": curuser, "longitude": devinfo.longitude,
						 "latitude": devinfo.latitude})
				elif devinfo.device_status == "OFFLINE" and (nowtime - lasttime).days >= 7:
					userdevices_offline_7d.append(
						{"device_name": devinfo.dev_name, "device_sn": devinfo.name, "device_desc": devinfo.description,
						 "device_status": devinfo.device_status, "last_updated": devinfo.last_updated,
						 "device_company": curuser, "longitude": devinfo.longitude,
						 "latitude": devinfo.latitude})
					userdevices_offline.append(
						{"device_name": devinfo.dev_name, "device_sn": devinfo.name, "device_desc": devinfo.description,
						 "device_status": devinfo.device_status, "last_updated": devinfo.last_updated,
						 "device_company": curuser, "longitude": devinfo.longitude,
						 "latitude": devinfo.latitude})
				else:
					userdevices_offline.append(
						{"device_name": devinfo.dev_name, "device_sn": devinfo.name, "device_desc": devinfo.description,
						 "device_status": devinfo.device_status, "last_updated": devinfo.last_updated,
						 "device_company": curuser, "longitude": devinfo.longitude,
						 "latitude": devinfo.latitude})

			pass
		pass

	if filter=="online":
		if userdevices_online:
			return userdevices_online
		else:
			return [{"device_name": "", "device_sn": "", "device_desc": "", "device_status": "",  "last_updated": "", "device_company": "",  "longitude": "", "latitude": ""}]
	elif filter=="offline":
		if userdevices_offline:
			return userdevices_offline
		else:
			return [{"device_name": "", "device_sn": "", "device_desc": "", "device_status": "",  "last_updated": "", "device_company": "",  "longitude": "", "latitude": ""}]
	elif filter=="offline_7d":
		if userdevices_offline_7d:
			return userdevices_offline_7d
		else:
			return [{"device_name": "", "device_sn": "", "device_desc": "", "device_status": "",  "last_updated": "", "device_company": "",  "longitude": "", "latitude": ""}]
	elif filter=="len_all":
		return len(userdevices)
	elif filter=="len_online":
		return len(userdevices_online)
	elif filter=="len_offline":
		return len(userdevices_offline)
	elif filter=="len_offline_7d":
		return len(userdevices_offline_7d)
	else:
		if userdevices:
			return userdevices
		else:
			return [{"device_name": "", "device_sn": "", "device_desc": "", "device_status": "",  "last_updated": "", "device_company": "",  "longitude": "", "latitude": ""}]




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
	return [user.name for user in users if user.name not in employees]

@frappe.whitelist()
def list_company_user(company):
	if 'Company Admin' not in frappe.get_roles(frappe.session.user):
		return False
	if frappe.db.get_value("Cloud Company", company, "enabled") != 1:
		return False
	return [d[0] for d in frappe.db.get_values("Cloud Employee", {"company": company})]

@frappe.whitelist()
def list_group_user(groupid):
	if 'Company Admin' not in frappe.get_roles(frappe.session.user):
		pass
	users = []
	for d in frappe.db.get_values("Cloud Company GroupUser", {"parent": groupid}, ["user", "role", "modified", "creation"]):
		users.append(d[0])
	return users


@frappe.whitelist()
def list_company_member(company):
	if 'Company Admin' not in frappe.get_roles(frappe.session.user):
		return False
	if frappe.db.get_value("Cloud Company", company, "enabled") != 1:
		return False
	return [{"member_id": d[0], "member_name": get_user_fullname(d[0])} for d in frappe.db.get_values("Cloud Employee", {"company": company})]


@frappe.whitelist()
def add_company_member():
	postdata = get_post_json_data()
	print(postdata)
	company = postdata.company
	members = postdata.members
	if not frappe.get_value("Cloud Company", {"name": company, "admin": frappe.session.user}):
		throw(_("You not the admin of company {0}").format(company))
	if 'Company Admin' in frappe.get_roles(frappe.session.user):
		added_user = []
		remained_users = []
		for m in members:
			comp = frappe.get_value("Cloud Employee", {"user": m}, "company")
			if comp:
				if comp != company:
					remained_users.append(m)
					#throw(_("User is in another company {0}").format(comp))
			else:
				doc = frappe.get_doc({"doctype": "Cloud Employee", "user": m, "company": company})
				doc.insert(ignore_permissions=True)
				frappe.db.commit()
				added_user.append(m)
		return {"added": added_user, "remained": remained_users, "result": 'sucessful'}

@frappe.whitelist()
def del_company_member():
	postdata = get_post_json_data()
	print(postdata)
	company = postdata.company
	members = postdata.members
	if 'Company Admin' in frappe.get_roles(frappe.session.user):
		if not frappe.get_value("Cloud Company", {"name": company, "admin": frappe.session.user}):
			return "You not the admin of company"
		else:
			deleted_user = []
			remained_users = []
			for m in members:
				try:
					frappe.delete_doc("Cloud Employee", m, ignore_permissions=True)
					deleted_user.append(m)
				except Exception as ex:
					remained_users.append(m)
			return {"deleted": deleted_user, "remained": remained_users, "result": 'sucessful'}

@frappe.whitelist()
def del_company_single_member():
	postdata = get_post_json_data()
	print(postdata)
	company = postdata.company
	member = postdata.member
	if 'Company Admin' in frappe.get_roles(frappe.session.user):
		if not frappe.get_value("Cloud Company", {"name": company, "admin": frappe.session.user}):
			return "You not the admin of company"
		else:
			try:
				frappe.delete_doc("Cloud Employee", member, ignore_permissions=True)
				return {"deleted": member, "result": 'sucessful'}
			except Exception as ex:
				return {"reason": ex, "result": 'failed'}

@frappe.whitelist()
def list_company_group(company):
	if 'Company Admin' not in frappe.get_roles(frappe.session.user):
		return False
	groupnames = [d[0] for d in frappe.db.get_values("Cloud Company Group", {"company": company})]
	groups = []
	for g in groupnames:
		gg = frappe.get_doc("Cloud Company Group", g)
		#print(gg.group_name.encode('utf-8'))
		groups.append({"group_name": gg.group_name, "name": gg.name})
	return groups

@frappe.whitelist()
def add_company_group():
	group = get_post_json_data()
	group.update({"doctype": "Cloud Company Group"})
	g = frappe.get_doc(group).insert()
	# gg = frappe.get_doc("Cloud Company Group", group)
	# print("newgroup", gg)
	nameobj = frappe.get_value("Cloud Employee", frappe.session.user, "company")
	company = frappe.get_doc('Cloud Company', nameobj).name
	groupnames = [d[0] for d in frappe.db.get_values("Cloud Company Group", {"company": company})]
	groups = []
	for g in groupnames:
		gg = frappe.get_doc("Cloud Company Group", g)
		#print(gg.group_name.encode('utf-8'))
		groups.append({"group_name": gg.group_name, "name": gg.name})
	return {"result": "sucessful", "groups": groups}

@frappe.whitelist()
def mod_company_group():
	group = get_post_json_data()
	g = frappe.get_doc("Cloud Company Group", group.name)
	g.set("group_name", group.group_name)
	g.save()
	return True

@frappe.whitelist()
def del_company_group(groupid):
	try:
		frappe.delete_doc("Cloud Company Group", groupid)
		return True
	except Exception as ex:
		return {"result": False, "reason": ex.message}


@frappe.whitelist()
def list_group_member(groupid):
	if 'Company Admin' not in frappe.get_roles(frappe.session.user):
		pass
	users = []
	# for d in frappe.db.get_values("Cloud Company GroupUser", {"parent": groupid}, ["user", "role", "modified", "creation"]):
	# 	users.append(_dict({"name": d[0], "role": d[1], "modified": d[2], "creation": d[3], "group": groupid}))
	for d in frappe.db.get_values("Cloud Company GroupUser", {"parent": groupid}, ["user", "role", "modified", "creation"]):
		users.append(_dict({"member_id": d[0], "member_name": get_user_fullname(d[0])}))
	if users:
		return users
	else:
		return {"member_id": "", "member_name": ""}

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
def add_group_members():
	postdata = get_post_json_data()
	print(postdata)
	group = postdata.group
	users = postdata.members
	g = frappe.get_doc("Cloud Company Group", group)
	g.add_users("User", *users)
	return {"result": 'sucessful'}

@frappe.whitelist()
def delete_group_members():
	postdata = get_post_json_data()
	print(postdata)
	group = postdata.group
	users = postdata.members
	g = frappe.get_doc("Cloud Company Group", group)
	g.remove_users(*users)
	return {"result": 'sucessful'}

@frappe.whitelist()
def query_iot_event(filter):
	gates = devices_list_array("all")
	events = []
	for g in gates:
		#print(g)
		if g["device_sn"]:
			print(g["device_sn"])
			rr = frappe.db.get_list("IOT Device Error", fields=["name", "device", "error_type", "error_key", "error_level", "error_info"], filters={"device": g["device_sn"],})
			if rr:
				for r in rr:
					events.append(r)

	ev_Visited = frappe.db.get_list("Error Visited", fields=["error_visited"], filters={"user": frappe.session.user, })
	ev_hasread = []
	ev_unread = []
	ev_Visited_list = []
	for d in ev_Visited:
		ev_Visited_list.append(d["error_visited"])

	if events:
		if ev_Visited_list:
			for e in events:
				f = e['name']
				if f in ev_Visited_list:
					e["hasRead"] = True
					e["brief"] = e["error_info"][0:32]
					ev_hasread.append(e)
				else:
					e["hasRead"] = False
					e["brief"] = e["error_info"][0:32]
					ev_unread.append(e)
		else:
			for e in events:
				e["hasRead"] = False
				e["brief"] = e["error_info"][0:32]
				ev_unread.append(e)

	events = ev_unread + ev_hasread

	if filter == "all":
		if events:
			return events
		else:
			return [{"name":None, "device":"No Data", "error_type":None, "error_key":None, "error_level":None, "error_info":None, "brief":None, "hasRead":True}]
	elif filter == "unread":
		if ev_unread:
			return ev_unread
		else:
			return [{"name": None, "device": "No Data", "error_type": None, "error_key": None, "error_level": None,
			         "error_info": None, "brief":None, "hasRead": True}]
	elif filter == "hasread":
		if ev_hasread:
			return ev_hasread
		else:
			return [{"name": None, "device":"No Data", "error_type": None, "error_key": None, "error_level": None,
			         "error_info": None, "brief":None, "hasRead": True}]
	elif filter == "len_all":
		return len(events)
	elif filter == "len_unread":
		return len(ev_unread)
	elif filter == "len_hasread":
		return len(ev_hasread)

@frappe.whitelist()
def get_iot_event(errid):
	event = frappe.get_doc("IOT Device Error", errid)
	return event

@frappe.whitelist()
def mark_iot_event_read():
	postdata = get_post_json_data()
	errid = postdata.errid
	print(errid)
	for id in errid:
		doc = frappe.get_doc({
			"doctype": "Error Visited",
			"error_visited": id,
			"user": frappe.session.user,
		}).insert()
	# doc.save()
	# frappe.db.commit()
	return {"result": 'sucessful'}

@frappe.whitelist()
def del_iot_event():
	postdata = get_post_json_data()
	print(postdata)
	company = postdata.company
	members = postdata.members

@frappe.whitelist(allow_guest=True)
def ping():
	form_data = frappe.form_dict
	if frappe.request and frappe.request.method == "POST":
		if form_data.data:
			form_data = json.loads(form_data.data)
		return form_data.get("text") or "No Text"
	return 'pong'