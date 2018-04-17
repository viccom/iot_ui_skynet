# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import json
import uuid
import requests
import redis
import datetime, time
import os
from frappe import _dict, throw, _
from iot.iot.doctype.iot_device.iot_device import IOTDevice
from iot.iot.doctype.iot_hdb_settings.iot_hdb_settings import IOTHDBSettings
from cloud.cloud.doctype.cloud_company_group.cloud_company_group import list_user_groups as _list_user_groups
from cloud.cloud.doctype.cloud_company.cloud_company import list_admin_companies, list_user_companies, list_users, get_domain
from frappe.desk.form.save import savedocs
from frappe.utils.user import get_user_fullname
from frappe.utils import now, get_datetime, convert_utc_to_user_timezone, now_datetime


def valid_auth_code(auth_code=None):
	auth_code = auth_code or frappe.get_request_header("HDB-AuthorizationCode")
	if not auth_code:
		throw(_("HDB-AuthorizationCode is required in HTTP Header!"))
	frappe.logger(__name__).debug(_("HDB-AuthorizationCode as {0}").format(auth_code))

	user = IOTHDBSettings.get_on_behalf(auth_code)
	if not user:
		throw(_("Authorization Code is incorrect!"))
	# form dict keeping
	form_dict = frappe.local.form_dict
	frappe.set_user(user)
	frappe.local.form_dict = form_dict

def list_iot_devices(user):
	# frappe.logger(__name__).debug(_("List Devices for user {0}").format(user))

	# Get Private Devices

	# pri_devices = frappe.db.get_values("IOT Device", {"owner_id": user, "owner_type": "User"})
	# print(pri_devices)
	ent_devices = []
	groups = _list_user_groups(user)
	for g in groups:
		g.group_name = frappe.get_value("Cloud Company Group", g.name, "group_name")
		gdev = [d[0] for d in
						frappe.db.get_values("IOT Device", {"owner_id": g.name, "owner_type": "Cloud Company Group"})]
		ent_devices = ent_devices + gdev
	pri_devices = [d[0] for d in
					frappe.db.get_values("IOT Device", {"owner_id": user, "owner_type": "User"})]

	# for c in bunch_codes:
	# 	pri_devices.append({"bunch": c, "sn": IOTDevice.list_device_sn_by_bunch(c)})
	devices = {"company_devices": ent_devices, "shared_devices": [], "private_devices": pri_devices}
	return devices

@frappe.whitelist()
def ping():
	return "Pong"

@frappe.whitelist(allow_guest=True)
def list_devices(user=None):
	"""
	List devices according to user specified in query params by naming as 'usr'
		this user is ERPNext user which you got from @iot.auth.login
	:param user: ERPNext username
	:return: device list
	"""
	# valid_auth_code()
	ssuser = frappe.session.user
	# user = user or frappe.form_dict.get('user')
	if not ssuser:
		throw(_("Query string user does not specified"))

	return list_iot_devices(ssuser)

@frappe.whitelist()
def userinfo_all(user):
	first_name, last_name, avatar, name, language, phone, mobile_no, last_login, last_ip = frappe.db.get_value("User",
		user, ["first_name", "last_name", "user_image", "name", "language", "phone", "mobile_no", "last_login", "last_ip"])
	return _dict({
		"code": 1000,
		"data":
			{
			"fullname": " ".join(filter(None, [first_name, last_name])),
			"avatar": avatar,
			"name": name,
			"language": language,
			"phone": phone,
			"mobile_no": mobile_no,
			"last_login": last_login,
			"last_ip": last_ip
			}
	})


@frappe.whitelist()
def iot_device_tree(sn=None):
	sn = sn or frappe.form_dict.get('sn')
	doc = frappe.get_doc('IOT Device', sn)
	doc.has_permission("read")
	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/11")
	subdevice = client.lrange(sn, 0, -1)
	subdevice.remove(sn)
	return subdevice


@frappe.whitelist()
def iot_device_cfg(sn=None, vsn=None):
	sn = sn or frappe.form_dict.get('sn')
	doc = frappe.get_doc('IOT Device', sn)
	doc.has_permission("read")
	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/10")
	cfg = client.get(vsn or sn)
	if cfg:
		return json.loads(cfg)
	else:
		return None

@frappe.whitelist()
def iot_is_beta(sn=None):
	iot_beta_flag = 0
	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/12")
	try:
		betainfo = client.hget(sn, 'enable_beta/value')
	except Exception as ex:
		return None
	if betainfo:
		iot_beta_flag = eval(betainfo)[1]
	return iot_beta_flag


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
def get_token():
	print("WWWWWWWWWWWW")
	csrf_token = frappe.sessions.get_csrf_token()
	frappe.db.commit()
	return csrf_token


@frappe.whitelist()
def list_company_user(company):
	if 'Company Admin' not in frappe.get_roles(frappe.session.user):
		return False
	if frappe.db.get_value("Cloud Company", company, "enabled") != 1:
		return False
	return [d[0] for d in frappe.db.get_values("Cloud Employee", {"company": company})]


@frappe.whitelist()
def company_admin(user):
	if 'Company Admin' not in frappe.get_roles(user):
		return False
	return _dict({
		"code": 1000,
		"data": list_admin_companies(user)
	})

@frappe.whitelist()
def list_company_member(company):
	if 'Company Admin' not in frappe.get_roles(frappe.session.user):
		return False
	if frappe.db.get_value("Cloud Company", company, "enabled") != 1:
		return False
	return [{"member_id": d[0], "member_name": get_user_fullname(d[0])} for d in frappe.db.get_values("Cloud Employee", {"company": company})]

@frappe.whitelist()
def add_newuser2company():
	postdata = get_post_json_data()
	company = postdata['company']
	userinfo = postdata['userinfo']
	userid = userinfo["email"]
	group = frappe.get_value("Cloud Company Group", {"company": company, "group_name": "root"})
	role = "user"
	user_exists = frappe.db.get_value("User", {"email": userid}, "email")
	print("@@@@@@@@@@@@@@@@", user_exists)
	if not user_exists:
		user = frappe.new_doc("User")
		user.update({
			"name": "New+User+1",
			"email": userinfo["email"],
			"language": "zh",
			"enabled": 1,
			"send_welcome_email": 0,
			"first_name": userinfo["first_name"],
			"last_name": userinfo["last_name"],
			"phone": userinfo["phone"],
			"mobile_no": userinfo["mobile_no"],
			"new_password": userinfo["new_password"]
		})
		user.insert()
	user_companies = list_user_companies(userid)
	if user_companies:
		if company in user_companies:
			return {"result": False, "info": userid + " has been an " + company +" Employee"}
		else:
			return {"result": False, "info": userid + " has been an other's company Employee"}
	if not frappe.get_value("Cloud Company", {"name": company, "admin": frappe.session.user}):
		throw(_("You not the admin of company {0}").format(company))
	if 'Company Admin' in frappe.get_roles(frappe.session.user):
		doc = frappe.get_doc({"doctype": "Cloud Employee", "user": userid, "company": company})
		doc.insert(ignore_permissions=True)
		g = frappe.get_doc("Cloud Company Group", group)
		g.add_users(role, userid)
		return {"result": True, "newuser": userid}

@frappe.whitelist()
def del_userfromcompany():
	postdata = get_post_json_data()
	company = postdata['company']
	users = postdata['users']
	group = frappe.get_value("Cloud Company Group", {"company": company, "group_name": "root"})
	if 'Company Admin' in frappe.get_roles(frappe.session.user):
		if not frappe.get_value("Cloud Company", {"name": company, "admin": frappe.session.user}):
			return "You not the admin of company"
		else:
			deleted_user = []
			remained_users = []
			for m in users:
				try:
					g = frappe.get_doc("Cloud Company Group", group)
					g.remove_users(m)
					frappe.delete_doc("Cloud Employee", m, ignore_permissions=True)
					# frappe.delete_doc("User", m)
					deleted_user.append(m)
				except Exception as ex:
					remained_users.append(m)
			return {"deleted": deleted_user, "remained": remained_users, "result": True}


@frappe.whitelist()
def update_userinfo():
	postdata = get_post_json_data()
	userid = postdata["userid"]
	user = frappe.get_doc("User", userid)
	user.update({
		"enabled": 1,
		"send_welcome_email": 0,
		"first_name": postdata["first_name"],
		"last_name": postdata["last_name"],
		"phone": postdata["phone"],
		"mobile_no": postdata["mobile_no"],
		"new_password": postdata["new_password"]
	})
	user.save()
	return {"result": True, "update_info": postdata}


@frappe.whitelist()
def devices_list(filter):
	curuser = frappe.session.user
	devices = list_iot_devices(curuser)
	#print(devices)
	userdevices = []
	userdevices_online = []
	userdevices_offline = []
	userdevices_offline_7d = []
	if devices["company_devices"]:
		for dsn in devices["company_devices"]:
			devinfo = IOTDevice.get_device_doc(dsn)
			# print(devinfo)
			# print(devinfo.name, devinfo.dev_name, devinfo.description, devinfo.device_status, devinfo.company)
			lasttime = get_datetime(devinfo.last_updated)
			nowtime = now_datetime()
			userdevices.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name, "device_desc": devinfo.description, "device_status": devinfo.device_status,  "last_updated": str(devinfo.last_updated)[:-7], "device_company": devinfo.company,  "longitude": devinfo.longitude, "latitude": devinfo.latitude, "beta": devinfo.use_beta, "iot_beta": iot_is_beta(dsn)})
			if devinfo.device_status == "ONLINE":
				userdevices_online.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name,
				                           "device_desc": devinfo.description,
				                           "device_status": devinfo.device_status,
				                           "last_updated": str(devinfo.last_updated)[:-7],
				                           "device_company": devinfo.company, "longitude": devinfo.longitude,
				                           "latitude": devinfo.latitude, "beta": devinfo.use_beta, "iot_beta": iot_is_beta(dsn)})
			elif devinfo.device_status == "OFFLINE" and (nowtime - lasttime).days >= 7:
				userdevices_offline_7d.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name,
				                               "device_desc": devinfo.description,
				                               "device_status": devinfo.device_status,
				                               "last_updated": str(devinfo.last_updated)[:-7],
				                               "device_company": devinfo.company,
				                               "longitude": devinfo.longitude, "latitude": devinfo.latitude, "beta": devinfo.use_beta, "iot_beta": iot_is_beta(dsn)})
				userdevices_offline.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name,
				                            "device_desc": devinfo.description,
				                            "device_status": devinfo.device_status,
				                            "last_updated": str(devinfo.last_updated)[:-7],
				                            "device_company": devinfo.company, "longitude": devinfo.longitude,
				                            "latitude": devinfo.latitude, "beta": devinfo.use_beta, "iot_beta": iot_is_beta(dsn)})
			else:
				userdevices_offline.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name,
				                            "device_desc": devinfo.description,
				                            "device_status": devinfo.device_status,
				                            "last_updated": str(devinfo.last_updated)[:-7],
				                            "device_company": devinfo.company, "longitude": devinfo.longitude,
				                            "latitude": devinfo.latitude, "beta": devinfo.use_beta, "iot_beta": iot_is_beta(dsn)})
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
					userdevices.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name, "device_desc": devinfo.description, "device_status": devinfo.device_status,  "last_updated": str(devinfo.last_updated)[:-7], "device_company": devinfo.company, "longitude": devinfo.longitude, "latitude": devinfo.latitude, "beta": devinfo.use_beta, "iot_beta": iot_is_beta(dsn)})
					if devinfo.device_status == "ONLINE":
						userdevices_online.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name,
						                           "device_desc": devinfo.description,
						                           "device_status": devinfo.device_status,
						                           "last_updated": str(devinfo.last_updated)[:-7],
						                           "device_company": devinfo.company, "longitude": devinfo.longitude,
						                           "latitude": devinfo.latitude, "beta": devinfo.use_beta, "iot_beta": iot_is_beta(dsn)})
					elif devinfo.device_status == "OFFLINE" and (nowtime - lasttime).days >= 7:
						userdevices_offline_7d.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name,
						                               "device_desc": devinfo.description,
						                               "device_status": devinfo.device_status,
						                               "last_updated": str(devinfo.last_updated)[:-7],
						                               "device_company": devinfo.company,
						                               "longitude": devinfo.longitude, "latitude": devinfo.latitude, "beta": devinfo.use_beta, "iot_beta": iot_is_beta(dsn)})
						userdevices_offline.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name,
						                            "device_desc": devinfo.description,
						                            "device_status": devinfo.device_status,
						                            "last_updated": str(devinfo.last_updated)[:-7],
						                            "device_company": devinfo.company, "longitude": devinfo.longitude,
						                            "latitude": devinfo.latitude, "beta": devinfo.use_beta, "iot_beta": iot_is_beta(dsn)})
					else:
						userdevices_offline.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name,
						                            "device_desc": devinfo.description,
						                            "device_status": devinfo.device_status,
						                            "last_updated": str(devinfo.last_updated)[:-7],
						                            "device_company": devinfo.company, "longitude": devinfo.longitude,
						                            "latitude": devinfo.latitude, "beta": devinfo.use_beta, "iot_beta": iot_is_beta(dsn)})

				pass
			pass
		pass

	if devices["private_devices"]:
		for dsn in devices["private_devices"]:
			devinfo = IOTDevice.get_device_doc(dsn)
			# print(dir(devinfo))
			# print(devinfo.name, devinfo.dev_name, devinfo.description, devinfo.device_status, devinfo.company)
			lasttime = get_datetime(devinfo.last_updated)
			nowtime = now_datetime()
			userdevices.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name, "device_desc": devinfo.description, "device_status": devinfo.device_status, "last_updated": str(devinfo.last_updated)[:-7],  "device_company": curuser, "longitude": devinfo.longitude, "latitude": devinfo.latitude, "beta": devinfo.use_beta, "iot_beta": iot_is_beta(dsn)})
			if devinfo.device_status == "ONLINE":
				userdevices_online.append(
					{"device_name": devinfo.dev_name, "device_sn": devinfo.name, "device_desc": devinfo.description,
					 "device_status": devinfo.device_status, "last_updated": str(devinfo.last_updated)[:-7],
					 "device_company": curuser, "longitude": devinfo.longitude,
					 "latitude": devinfo.latitude, "beta": devinfo.use_beta, "iot_beta": iot_is_beta(dsn)})
			elif devinfo.device_status == "OFFLINE" and (nowtime - lasttime).days >= 7:
				userdevices_offline_7d.append(
					{"device_name": devinfo.dev_name, "device_sn": devinfo.name, "device_desc": devinfo.description,
					 "device_status": devinfo.device_status, "last_updated": str(devinfo.last_updated)[:-7],
					 "device_company": curuser, "longitude": devinfo.longitude,
					 "latitude": devinfo.latitude, "beta": devinfo.use_beta, "iot_beta": iot_is_beta(dsn)})
				userdevices_offline.append(
					{"device_name": devinfo.dev_name, "device_sn": devinfo.name, "device_desc": devinfo.description,
					 "device_status": devinfo.device_status, "last_updated": str(devinfo.last_updated)[:-7],
					 "device_company": curuser, "longitude": devinfo.longitude,
					 "latitude": devinfo.latitude, "beta": devinfo.use_beta, "iot_beta": iot_is_beta(dsn)})
			else:
				userdevices_offline.append(
					{"device_name": devinfo.dev_name, "device_sn": devinfo.name, "device_desc": devinfo.description,
					 "device_status": devinfo.device_status, "last_updated": str(devinfo.last_updated)[:-7],
					 "device_company": curuser, "longitude": devinfo.longitude,
					 "latitude": devinfo.latitude, "beta": devinfo.use_beta, "iot_beta": iot_is_beta(dsn)})

		pass

	rdict = {}
	rdict["code"] = 1000
	if filter =="online":
		if userdevices_online:
			rdict["data"] = userdevices_online
		return rdict
	elif filter =="offline":
		if userdevices_offline:
			rdict["data"] = userdevices_offline
		return rdict
	elif filter =="offline_7d":
		if userdevices_offline_7d:
			rdict["data"] = userdevices_offline_7d
		return rdict
	elif filter == "len_all":
		return len(userdevices)
	elif filter == "len_online":
		return len(userdevices_online)
	elif filter == "len_offline":
		return len(userdevices_offline)
	elif filter =="len_offline_7d":
		return len(userdevices_offline_7d)
	elif filter =="devices_amount":
		return {"all":len(userdevices), "online":len(userdevices_online), "offline":len(userdevices_offline), "offline_7d":len(userdevices_offline_7d)}
	else:
		if userdevices:
			rdict["data"] = userdevices
		return rdict


@frappe.whitelist()
def enable_beta(sn):
	doc = frappe.get_doc("IOT Device", sn);
	doc.set_use_beta()
	from iot.device_api import send_action
	return send_action("sys", action="enable/beta", device=sn, data="1")

@frappe.whitelist()
def add_new_gate(sn, name, desc, owner_type):
	type = "User"
	owner = frappe.session.user
	user_id = frappe.session.user
	company = list_user_companies(user_id)[0]
	groupid = None
	if company:
		try:
			groupid = frappe.get_value("Cloud Company Group", {"company": company, "group_name": "root"})
		except Exception as ex:
			print(ex)
	if owner_type == 2:
		type = "Cloud Company Group"
		owner = groupid
	sn_exists = frappe.db.get_value("IOT Device", {"sn": sn}, "sn")
	if sn_exists:
		if company:
			try:
				iot_device = frappe.get_doc("IOT Device", sn)
			except Exception as ex:
				print(ex)
		if iot_device.owner_type:
			if iot_device.owner_type == "User" and iot_device.owner_id == user_id:
				return {"result": False, "info": sn + "'s owner is u"}
			if iot_device.owner_type == "User" and iot_device.owner_id != user_id:
				if iot_device.owner_id:
					return {"result": False, "info": sn + "'s owner is not u"}
			if iot_device.owner_type == "Cloud Company Group" and iot_device.owner_id == groupid:
				return {"result": False, "info": sn + "'s owner is "+company}
			if iot_device.owner_type == "Cloud Company Group" and iot_device.owner_id != groupid:
				if iot_device.owner_id:
					return {"result": False, "info": sn + "'s owner is not u"}
		else:
			try:
				iot_device.update_owner(type, owner)
			except Exception as ex:
				print(ex)
			return {"result": True, "info": sn}
	else:
		doc = frappe.get_doc({"doctype": "IOT Device", "sn": sn, "dev_name": name, "description": desc, "owner_type": type, "owner_id": owner})
		doc.insert(ignore_permissions=True)
		return {"result": True, "info": sn}

@frappe.whitelist()
def remove_gate(sn):
	try:
		doc = frappe.get_doc("IOT Device", sn)
		doc.update_owner("", None)
		return {"result": True, "sn": sn}
	except Exception as ex:
		print(ex)
		return False


@frappe.whitelist()
def update_gate(sn, name, desc):
	try:
		doc = frappe.get_doc("IOT Device", sn)
		doc.update({
			"dev_name": name,
			"description": desc
		})
		doc.save()
		return {"result": True, "sn": sn}
	except Exception as ex:
		print(ex)
		return False

@frappe.whitelist()
def gate_info(sn):
	try:
		device = frappe.get_doc('IOT Device', sn)
		device.has_permission('read')
		gate = {}
		gate['code'] = 1000
		gate['data'] = {}
		gate['data']['basic'] = {}
		gate['data']['config'] = {}
		gate['data']['applist'] = {}
		gate['data']['basic']['sn'] = device.sn
		gate['data']['basic']['model'] = "Q102"
		gate['data']['basic']['name'] = device.dev_name
		gate['data']['basic']['desc'] = device.description
		gate['data']['basic']['company'] = device.company
		gate['data']['basic']['Location'] = device.sn
		gate['data']['basic']['beta'] = device.use_beta
		gate['data']['basic']['status'] = device.device_status
		client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/12")
		if client.exists(sn):
			if client.hget(sn, "version/value"):
				gate['data']['config']['iot_version'] = eval(client.hget(sn, "version/value"))[1]
			if client.hget(sn, "skynet_version/value"):
				gate['data']['config']['skynet_version'] = eval(client.hget(sn, "skynet_version/value"))[1]
			if client.hget(sn, "starttime/value"):
				_starttime = eval(client.hget(sn, "starttime/value"))[1]
				gate['data']['config']['starttime'] = str(
					convert_utc_to_user_timezone(datetime.datetime.utcfromtimestamp(int(_starttime))).replace(
						tzinfo=None))
			if client.hget(sn, "uptime/value"):
				gate['data']['config']['uptime'] = int(eval(client.hget(sn, "uptime/value"))[1] / 1000)
			if client.hget(sn, "skynet_platform/value"):
				gate['data']['config']['skynet_platform'] = eval(client.hget(sn, "skynet_platform/value"))[1]
			s = requests.Session()
			s.auth = ("api", "Pa88word")
			r = s.get('http://127.0.0.1:18083/api/v2/nodes/emq@127.0.0.1/clients/' + sn)
			rdict = json.loads(r.text)
			gate['data']['config']['public_ip'] = rdict['result']['objects'][0]['ipaddress']
			gate['data']['config']['public_port'] = rdict['result']['objects'][0]['port']
			gate['data']['config']['cpu'] = "imx6ull 528MHz"
			gate['data']['config']['ram'] = "256 MB"
			gate['data']['config']['rom'] = "4 GB"
			gate['data']['config']['os'] = "openwrt"
			client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/6")
			gate['data']['applist'] = json.loads(client.get(sn))
			return gate
	except Exception as ex:
		print(ex)
		return False


@frappe.whitelist()
def iot_applist(sn=None):
	if sn:
		client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/6")
		applist = json.loads(client.get(sn))
		iot_applist = []
		for app in applist:
			filters = {"app": applist[app]['name']}
			cloud_ver = None
			owner = None
			fork_app = None
			fork_ver =None
			cloud_appname = None
			try:
				lastver = frappe.db.get_all("IOT Application Version", "*", filters, order_by="version").pop()
				if lastver:
					cloud_ver = lastver.version
					cloud_appname = lastver.app_name
					owner = lastver.owner
			except Exception as ex:
				pass
			try:
				doc = frappe.get_doc("IOT Application", applist[app]['name'])
				# print(dir(doc))
				if doc:
					fork_app = doc.get_fork(frappe.session.user, cloud_ver)
					# print(fork_app)
					from app_center.app_center.doctype.iot_application_version.iot_application_version import IOTApplicationVersion
					fork_ver = IOTApplicationVersion.get_latest_version(fork_app)
					# print(fork_ver)
			except Exception as ex:
				pass
			# fork_app = doc.get_fork(owner, cloud_ver)
			# fork_ver = IOTApplicationVersion.get_latest_version(app)
			# print(fork_app, fork_ver)
			a = {"name": app, "cloudname": applist[app]['name'], "cloud_appname": cloud_appname, "iot_ver": int(applist[app]['version']), "cloud_ver": cloud_ver, "owner":owner, "fork_app": fork_app, "fork_ver": fork_ver}
			iot_applist.append(a)
		return {"code": 1000, "data": iot_applist}
	else:
		return None


@frappe.whitelist()
def iot_app_dev_tree(sn=None):
	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/6")
	applist = json.loads(client.get(sn))
	device_tree = iot_device_tree(sn)
	app_dev_tree = {}
	for app in applist:
		app_dev_tree[app] = []
		for devsn in device_tree:
			devmeta = iot_device_cfg(sn, devsn)['meta']
			if devmeta['app']==app:
				devmeta['sn']=devsn
				app_dev_tree[app].append(devmeta)
			pass
		pass
	return {"code": 1000, "data": app_dev_tree}


@frappe.whitelist()
def iot_device_data_array(sn=None, vsn=None):
	sn = sn or frappe.form_dict.get('sn')
	vsn = vsn or sn
	doc = frappe.get_doc('IOT Device', sn)
	doc.has_permission("read")

	if vsn != sn:
		if vsn not in iot_device_tree(sn):
			return ""

	cfg = iot_device_cfg(sn, vsn)
	if not cfg:
		return ""
	# print(cfg)
	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/12")
	hs = client.hgetall(vsn)
	data = []
	if cfg.has_key("inputs"):
		tags = cfg.get("inputs")
		for tag in tags:
			name = tag.get('name')
			valuegroup = hs.get(name + "/value")
			if valuegroup:
				# print("vvvvvv:",valuegroup)
				vlist = eval(valuegroup)
				timestr = ''
				if vlist:
					timestr = str(
						convert_utc_to_user_timezone(datetime.datetime.utcfromtimestamp(int(vlist[0]))).replace(
							tzinfo=None))
				data.append({"name": name, "pv": vlist[1], "tm": timestr, "vt": tag.get("vt"), "q": vlist[2], "desc": tag.get("desc") })
	return {"code": 1000, "data": data}


UTC_FORMAT1 = "%Y-%m-%dT%H:%M:%S.%fZ"
UTC_FORMAT2 = "%Y-%m-%dT%H:%M:%SZ"


def utc2local(utc_st):
	now_stamp = time.time()
	local_time = datetime.datetime.fromtimestamp(now_stamp)
	utc_time = datetime.datetime.utcfromtimestamp(now_stamp)
	offset = local_time - utc_time
	local_st = utc_st + offset
	return local_st

@frappe.whitelist()
def taghisdata(sn=None, vsn=None, vt=None, tag=None, condition=None):
	vsn = vsn or sn
	vtdict = {"float": "value", "int": "int_value", "string": "string_value"}
	vt = vt or "float"
	fields = '"' + vtdict.get(vt) + '"' + ' , "quality"'
	doc = frappe.get_doc('IOT Device', sn)
	doc.has_permission("read")

	inf_server = IOTHDBSettings.get_influxdb_server()
	if not inf_server:
		frappe.logger(__name__).error("InfluxDB Configuration missing in IOTHDBSettings")
		return 500
	query = 'SELECT ' + fields + ' FROM "' + tag + '"'
	if condition:
		query = query + ' WHERE  ' + condition + ' AND "iot"=\'' + sn + '\' AND "device"=\'' + vsn + '\'' + ' LIMIT 100'
	else:
		query = query + ' WHERE  ' + '"iot"=\'' + sn + '\' AND "device"=\'' + vsn + '\'' + ' LIMIT 100'
	# print("query:", query)
	domain = frappe.get_value("Cloud Company", doc.company, "domain")
	r = requests.session().get(inf_server + "/query", params={"q": query, "db": domain}, timeout=10)
	if r.status_code == 200:
		# return r.json()
		try:
			res = r.json()["results"][0]['series'][0]['values']
			taghis = []
			for i in range(0, len(res)):
				hisvalue = {}
				# print('*********', res[i][0])
				try:
					utc_time = datetime.datetime.strptime(res[i][0], UTC_FORMAT1)
				except Exception as err:
					pass
				try:
					utc_time = datetime.datetime.strptime(res[i][0], UTC_FORMAT2)
				except Exception as err:
					pass
				# local_time = utc2local(utc_time).strftime("%Y-%m-%d %H:%M:%S")
				local_time = str(convert_utc_to_user_timezone(utc_time).replace(tzinfo=None))
				hisvalue = {'name': tag, 'value': res[i][1], 'time': local_time, 'quality': res[i][2], 'vsn': vsn}
				taghis.append(hisvalue)
			#print(taghis)
			return {"code": 1000, "data": taghis}
		except Exception as err:
			return r.json()

@frappe.whitelist()
def appstore_applist(category=None, protocol=None, device_supplier=None, user=None, name=None, app_name=None):
	filters = {"owner": ["!=", "Administrator"]}
	if user:
		filters = {"owner": user}
	if category:
		filters["category"] = category
	if protocol:
		filters["protocol"] = protocol
	if device_supplier:
		filters["device_supplier"] = device_supplier
	if name:
		filters["name"] = name
	if app_name:
		filters["app_name"] = app_name
	apps = frappe.db.get_all("IOT Application", "*", filters, order_by="modified desc")
	return {"code": 1000, "data": apps}


@frappe.whitelist()
def appstore_category():

	return None

@frappe.whitelist()
def appstore_supplier():
	return None

@frappe.whitelist()
def appstore_protocol():
	return None

@frappe.whitelist()
def app_details(app_name):
	try:
		doc = frappe.get_doc('IOT Application', app_name)
		return {"code": 1000, "data": doc}
	except Exception as ex:
		print(ex)
		return False