# -*- coding: UTF-8 -*-
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
from iot.user_api import valid_auth_code
from cloud.cloud.doctype.cloud_company.cloud_company import list_admin_companies, list_user_companies, list_users, get_domain
from app_center.api import get_latest_version
from frappe.utils.user import get_user_fullname
from frappe.utils import get_fullname
from frappe.utils import now, get_datetime, convert_utc_to_user_timezone, now_datetime


@frappe.whitelist(allow_guest=True)
def ping():
	return "Pong"

@frappe.whitelist()
def list_devices(user):
	from iot.hdb_api import list_devices as _list_devices
	return _list_devices(user)


@frappe.whitelist()
def userinfo_all(user):
	if 'Company Admin' not in frappe.get_roles(frappe.session.user):
		return False
	admin_companies = list_admin_companies(frappe.session.user)
	for company in admin_companies:
		if frappe.get_value('Cloud Employee', user, 'company') == company:
			return frappe.db.get_value("User", user, as_dict=True, fieldname=["first_name", "last_name", "user_image", "name", "language", "phone", "mobile_no", "last_login", "last_ip"])


@frappe.whitelist()
def gate_device_tree(sn):
	from iot.hdb import iot_device_tree as _iot_device_tree
	subdevice = _iot_device_tree(sn)
	if subdevice:
		subdevice.remove(sn)
	return subdevice


@frappe.whitelist(allow_guest=True)
def gate_device_cfg(sn, vsn=None):
	valid_auth_code()
	from iot.hdb import iot_device_cfg as _iot_device_cfg
	return _iot_device_cfg(sn, vsn)


@frappe.whitelist()
def gate_is_beta(sn):
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
def company_admin():
	user = frappe.session.user
	if 'Company Admin' not in frappe.get_roles(user):
		return {"admin": False}
	return _dict({
		"admin": True,
		"companies": list_admin_companies(user)
	})


def valid_company_admin(company):
	if 'Company Admin' not in frappe.get_roles(frappe.session.user) \
			or not frappe.get_value("Cloud Company", {"name": company, "admin": frappe.session.user, "enabled": 1}):
		throw(_("You not the admin of company {0}").format(company))

@frappe.whitelist(allow_guest=True)
def get_company_default_group(company):
	valid_auth_code()
	valid_company_admin(company)
	return frappe.get_value("Cloud Company Group", {"company": company, "group_name": "root"})


@frappe.whitelist(allow_guest=True)
def get_company_groups(company):
	valid_auth_code()
	valid_company_admin(company)
	groups = frappe.get_all("Cloud Company Group", {"company": company}, ["name", "group_name"])
	# groups = [d[0] for d in frappe.db.get_values("Cloud Company Group", {"company": company})]
	return groups



@frappe.whitelist()
def list_company_member(company):
	valid_company_admin(company)
	return [{"user": d[0], "fullname": get_user_fullname(d[0])} for d in frappe.db.get_values("Cloud Employee", {"company": company})]


@frappe.whitelist()
def add_newuser2company():
	postdata = get_post_json_data()
	company = postdata['company']
	userinfo = postdata['userinfo']
	userid = userinfo["email"]

	valid_company_admin(company)
	group = get_company_default_group(company)
	if not group:
		throw(_("Default group is not found"))

	role = "user"
	user_exists = frappe.db.get_value("User", {"email": userid}, "email")
	if not user_exists:
		frappe.logger(__name__).debug(_("Creating user {0} for company {1}").format(userid, company))
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
		user.insert(ignore_permissions=True)

	doc = frappe.get_doc({"doctype": "Cloud Employee", "user": userid, "company": company})
	doc.insert(ignore_permissions=True)
	g = frappe.get_doc("Cloud Company Group", group)
	g.add_users(role, userid)
	return {"userid": userid}


@frappe.whitelist()
def del_userfromcompany():
	postdata = get_post_json_data()
	company = postdata['company']
	users = postdata['users']

	valid_company_admin(company)
	group = get_company_default_group(company)

	deleted_users = []
	remained_users = []
	for user in users:
		try:
			g = frappe.get_doc("Cloud Company Group", group)
			g.remove_users(user)
			frappe.delete_doc("Cloud Employee", user, ignore_permissions=True)
			deleted_users.append(user)
		except Exception as ex:
			remained_users.append(user)
	return {"deleted": deleted_users, "remained": remained_users}


@frappe.whitelist()
def update_userinfo():
	postdata = get_post_json_data()
	userid = postdata["userid"]
	company = frappe.get_value("Cloud Employee", userid, "company")
	if not company:
		throw(_("Invalid employee id {0}").format(userid))

	valid_company_admin(company)

	user = frappe.get_doc("User", userid)
	user.update({
		"send_welcome_email": 0,
		"first_name": postdata["first_name"],
		"last_name": postdata["last_name"],
		"phone": postdata["phone"],
		"mobile_no": postdata["mobile_no"],
	})
	if postdata.has_key('enable'):
		user.update({"enable": postdata.get('enabled')})
	if postdata.has_key('new_password'):
		user.update({"new_password": postdata["new_password"]})

	user.save(ignore_permissions=True)
	return { "userid": userid }



@frappe.whitelist()
def user_company():
	company = frappe.get_value("Cloud Employee", frappe.session.user, "company")
	if not company:
		return False
	else:
		return {"company": company}

@frappe.whitelist()
def verify_password(password):
	from frappe.utils.password import check_password
	try:
		# returns user in correct case
		return check_password(frappe.session.user, password)
	except frappe.AuthenticationError:
		throw(_("Incorrect password"))


@frappe.whitelist(allow_guest=True)
def devices_list(filter):
	from iot.hdb_api import list_iot_devices as _list_iot_devices
	valid_auth_code()
	curuser = frappe.session.user
	devices = _list_iot_devices(curuser)
	userdevices = []
	userdevices_online = []
	userdevices_offline = []
	userdevices_offline_7d = []
	company_devices = devices.get('company_devices')
	client_6 = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/6", decode_responses=True)
	client_11 = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/11", decode_responses=True)
	if company_devices:
		for group in company_devices:
			for dsn in group["devices"]:
				dsn = dsn.strip()
				devinfo = IOTDevice.get_device_doc(dsn)
				appsnum = 0
				devsnum = 0


				try:
					appsnum = len(json.loads(client_6.get(dsn)))
				except Exception as ex:
					frappe.logger(__name__).error(ex)
					pass
				try:
					devsnum = client_11.llen(dsn)
				except Exception as ex:
					frappe.logger(__name__).error(ex)
					pass
				# print(devinfo)
				# print(devinfo.name, devinfo.dev_name, devinfo.description, devinfo.device_status, devinfo.company)
				lasttime = get_datetime(devinfo.last_updated)
				nowtime = now_datetime()
				userdevices.append({"device_name": devinfo.dev_name,
				                    "device_sn": devinfo.name,
				                    "device_desc": devinfo.description,
				                    "device_status": devinfo.device_status,
				                    "device_apps_num": appsnum,
				                    "device_devs_num": devsnum,
				                    "last_updated": str(devinfo.last_updated)[:-7],
				                    "device_company": devinfo.company,
				                    "longitude": devinfo.longitude,
				                    "latitude": devinfo.latitude,
				                    "beta": devinfo.use_beta,
				                    "iot_beta": gate_is_beta(dsn)})
				if devinfo.device_status == "ONLINE":
					userdevices_online.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name,
											   "device_desc": devinfo.description,
											   "device_status": devinfo.device_status,
					                           "device_apps_num": appsnum,
					                           "device_devs_num": devsnum,
											   "last_updated": str(devinfo.last_updated)[:-7],
											   "device_company": devinfo.company, "longitude": devinfo.longitude,
											   "latitude": devinfo.latitude, "beta": devinfo.use_beta, "iot_beta": gate_is_beta(dsn)})
				elif devinfo.device_status == "OFFLINE" and (nowtime - lasttime).days >= 7:
					userdevices_offline_7d.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name,
												   "device_desc": devinfo.description,
												   "device_status": devinfo.device_status,
												   "device_apps_num": appsnum,
												   "device_devs_num": devsnum,
												   "last_updated": str(devinfo.last_updated)[:-7],
												   "device_company": devinfo.company,
												   "longitude": devinfo.longitude, "latitude": devinfo.latitude, "beta": devinfo.use_beta, "iot_beta": gate_is_beta(dsn)})
					userdevices_offline.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name,
												"device_desc": devinfo.description,
												"device_status": devinfo.device_status,
												"device_apps_num": appsnum,
												"device_devs_num": devsnum,
												"last_updated": str(devinfo.last_updated)[:-7],
												"device_company": devinfo.company, "longitude": devinfo.longitude,
												"latitude": devinfo.latitude, "beta": devinfo.use_beta, "iot_beta": gate_is_beta(dsn)})
				else:
					userdevices_offline.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name,
												"device_desc": devinfo.description,
												"device_status": devinfo.device_status,
												"device_apps_num": appsnum,
												"device_devs_num": devsnum,
												"last_updated": str(devinfo.last_updated)[:-7],
												"device_company": devinfo.company, "longitude": devinfo.longitude,
												"latitude": devinfo.latitude, "beta": devinfo.use_beta, "iot_beta": gate_is_beta(dsn)})

	shared_devices = devices.get("shared_devices")
	if shared_devices:
		for group in shared_devices:
			for dsn in group["devices"]:
				dsn = dsn.strip()
				devinfo = IOTDevice.get_device_doc(dsn)
				appsnum = 0
				devsnum = 0
				try:
					appsnum = len(json.loads(client_6.get(dsn)))
				except Exception as ex:
					frappe.logger(__name__).error(ex)
					pass
				try:
					devsnum = client_11.llen(dsn)
				except Exception as ex:
					frappe.logger(__name__).error(ex)
					pass
				#print(dir(devinfo))
				#print(devinfo.name, devinfo.dev_name, devinfo.description, devinfo.device_status, devinfo.company)
				lasttime = get_datetime(devinfo.last_updated)
				nowtime = now_datetime()
				userdevices.append({"device_name": devinfo.dev_name,
				                    "device_sn": devinfo.name,
				                    "device_desc": devinfo.description,
				                    "device_status": devinfo.device_status,
				                    "device_apps_num": appsnum,
				                    "device_devs_num": devsnum,
				                    "last_updated": str(devinfo.last_updated)[:-7],
				                    "device_company": devinfo.company,
				                    "longitude": devinfo.longitude,
				                    "latitude": devinfo.latitude,
				                    "beta": devinfo.use_beta,
				                    "iot_beta": gate_is_beta(dsn)})
				if devinfo.device_status == "ONLINE":
					userdevices_online.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name,
											   "device_desc": devinfo.description,
											   "device_status": devinfo.device_status,
												"device_apps_num": appsnum,
												"device_devs_num": devsnum,
											   "last_updated": str(devinfo.last_updated)[:-7],
											   "device_company": devinfo.company, "longitude": devinfo.longitude,
											   "latitude": devinfo.latitude, "beta": devinfo.use_beta, "iot_beta": gate_is_beta(dsn)})
				elif devinfo.device_status == "OFFLINE" and (nowtime - lasttime).days >= 7:
					userdevices_offline_7d.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name,
												   "device_desc": devinfo.description,
												   "device_status": devinfo.device_status,
												"device_apps_num": appsnum,
												"device_devs_num": devsnum,
												   "last_updated": str(devinfo.last_updated)[:-7],
												   "device_company": devinfo.company,
												   "longitude": devinfo.longitude, "latitude": devinfo.latitude, "beta": devinfo.use_beta, "iot_beta": gate_is_beta(dsn)})
					userdevices_offline.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name,
												"device_desc": devinfo.description,
												"device_status": devinfo.device_status,
												"device_apps_num": appsnum,
												"device_devs_num": devsnum,
												"last_updated": str(devinfo.last_updated)[:-7],
												"device_company": devinfo.company, "longitude": devinfo.longitude,
												"latitude": devinfo.latitude, "beta": devinfo.use_beta, "iot_beta": gate_is_beta(dsn)})
				else:
					userdevices_offline.append({"device_name": devinfo.dev_name, "device_sn": devinfo.name,
												"device_desc": devinfo.description,
												"device_status": devinfo.device_status,
												"device_apps_num": appsnum,
												"device_devs_num": devsnum,
												"last_updated": str(devinfo.last_updated)[:-7],
												"device_company": devinfo.company, "longitude": devinfo.longitude,
												"latitude": devinfo.latitude, "beta": devinfo.use_beta, "iot_beta": gate_is_beta(dsn)})

	private_devices = devices.get("private_devices")
	if private_devices:
		for dsn in private_devices:
			dsn = dsn.strip()
			devinfo = IOTDevice.get_device_doc(dsn)
			appsnum = 0
			devsnum = 0
			try:
				appsnum = len(json.loads(client_6.get(dsn)))
			except Exception as ex:
				frappe.logger(__name__).error(ex)
				pass
			try:
				devsnum = client_11.llen(dsn)
			except Exception as ex:
				frappe.logger(__name__).error(ex)
				pass
			# print(dir(devinfo))
			# print(devinfo.name, devinfo.dev_name, devinfo.description, devinfo.device_status, devinfo.company)
			lasttime = get_datetime(devinfo.last_updated)
			nowtime = now_datetime()
			userdevices.append({"device_name": devinfo.dev_name,
			                    "device_sn": devinfo.name,
			                    "device_desc": devinfo.description,
			                    "device_status": devinfo.device_status,
			                    "device_apps_num": appsnum,
			                    "device_devs_num": devsnum,
			                    "last_updated": str(devinfo.last_updated)[:-7],
			                    "device_company": curuser,
			                    "longitude": devinfo.longitude,
			                    "latitude": devinfo.latitude,
			                    "beta": devinfo.use_beta,
			                    "iot_beta": gate_is_beta(dsn)})
			if devinfo.device_status == "ONLINE":
				userdevices_online.append(
					{"device_name": devinfo.dev_name, "device_sn": devinfo.name, "device_desc": devinfo.description,
					 "device_status": devinfo.device_status,
					"device_apps_num": appsnum,
					"device_devs_num": devsnum,
					 "last_updated": str(devinfo.last_updated)[:-7],
					 "device_company": curuser,
					 "longitude": devinfo.longitude,
					 "latitude": devinfo.latitude,
					 "beta": devinfo.use_beta,
					 "iot_beta": gate_is_beta(dsn)})
			elif devinfo.device_status == "OFFLINE" and (nowtime - lasttime).days >= 7:
				userdevices_offline_7d.append(
					{"device_name": devinfo.dev_name, "device_sn": devinfo.name, "device_desc": devinfo.description,
					 "device_status": devinfo.device_status,
					"device_apps_num": appsnum,
					"device_devs_num": devsnum,
                     "last_updated": str(devinfo.last_updated)[:-7],
					 "device_company": curuser, "longitude": devinfo.longitude,
					 "latitude": devinfo.latitude, "beta": devinfo.use_beta, "iot_beta": gate_is_beta(dsn)})
				userdevices_offline.append(
					{"device_name": devinfo.dev_name, "device_sn": devinfo.name, "device_desc": devinfo.description,
					 "device_status": devinfo.device_status,
					"device_apps_num": appsnum,
					"device_devs_num": devsnum,"last_updated": str(devinfo.last_updated)[:-7],
					 "device_company": curuser, "longitude": devinfo.longitude,
					 "latitude": devinfo.latitude, "beta": devinfo.use_beta, "iot_beta": gate_is_beta(dsn)})
			else:
				userdevices_offline.append(
					{"device_name": devinfo.dev_name, "device_sn": devinfo.name, "device_desc": devinfo.description,
					 "device_status": devinfo.device_status,
					"device_apps_num": appsnum,
					"device_devs_num": devsnum,
                     "last_updated": str(devinfo.last_updated)[:-7],
					 "device_company": curuser, "longitude": devinfo.longitude,
					 "latitude": devinfo.latitude, "beta": devinfo.use_beta, "iot_beta": gate_is_beta(dsn)})


	if filter =="online":
		if len(userdevices_online) == 0:
			frappe.response['message'] = []
			return
		return userdevices_online
	elif filter =="offline":
		if len(userdevices_offline) == 0:
			frappe.response['message'] = []
			return
		return userdevices_offline
	elif filter =="offline_7d":
		if len(userdevices_offline_7d) == 0:
			frappe.response['message'] = []
			return
		return userdevices_offline_7d
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
		if len(userdevices) == 0:
			frappe.response['message'] = []
			return
		return userdevices or []


@frappe.whitelist()
def enable_beta(sn):
	doc = frappe.get_doc("IOT Device", sn)
	doc.set_use_beta()
	from iot.device_api import send_action
	return send_action("sys", action="enable/beta", device=sn, data="1")


@frappe.whitelist()
def new_virtual_gate():
	if frappe.request.method != "POST":
		throw(_("Request Method Must be POST!"))
	doc = frappe.get_doc({
		"doctype": "IOT Virtual Device",
		"user": frappe.session.user,
		"sn": str(uuid.uuid1()).upper(),
	}).insert()
	return doc.name


@frappe.whitelist()
def add_new_gate(sn, name, desc, owner_type):
	type = "User"
	owner = frappe.session.user
	if owner_type == 2:
		company = list_user_companies(frappe.session.user)[0]
		try:
			owner = frappe.get_value("Cloud Company Group", {"company": company, "group_name": "root"})
			type = "Cloud Company Group"
		except Exception as ex:
			throw(_("Cannot find default group in company{0}. Error: {1}").format(company, repr(ex)))

	iot_device = None
	sn_exists = frappe.db.get_value("IOT Device", {"sn": sn}, "sn")
	if not sn_exists:
		iot_device = frappe.get_doc({"doctype": "IOT Device", "sn": sn, "dev_name": name, "description": desc, "owner_type": type, "owner_id": owner})
		iot_device.insert(ignore_permissions=True)
	else:
		iot_device = frappe.get_doc("IOT Device", sn)

	if iot_device.owner_id:
		if iot_device.owner_id == owner and iot_device.owner_type == type:
			return True
		throw(_("Device {0} is owned by {1}").format(sn, iot_device.owner_id))
	else:
		iot_device.set("dev_name", name)
		iot_device.set("description", desc)
		iot_device.update_owner(type, owner)
		return True


@frappe.whitelist(allow_guest=True)
def Batch_entry_gates():
	valid_auth_code()
	postdata = get_post_json_data()
	gates = postdata['gates']
	company = postdata['company']
	group = postdata['group']
	if not group:
		group = "root"
	owner = ''
	owntype = ''
	if company:
		owner = frappe.get_value("Cloud Company Group", {"company": company, "group_name": group})
		if owner:
			owntype = "Cloud Company Group"
	exec_result = {}
	for gate in gates:
		iot_device = None
		if not gate['name']:
			gate['name'] = gate['sn'] + '_name'
		if not gate['desc']:
			gate['desc'] = gate['sn'] + '_desc'
		sn_exists = frappe.db.get_value("IOT Device", {"sn": gate['sn']}, "sn")
		if not sn_exists:
			iot_device = frappe.get_doc(
				{"doctype": "IOT Device", "sn": gate['sn'], "dev_name": gate['name'], "description": gate['desc'], "owner_type": owntype,
				 "owner_id": owner})
			iot_device.insert(ignore_permissions=True)
			exec_result[gate['sn']] = 1
		else:
			exec_result[gate['sn']] = 2
	return exec_result

@frappe.whitelist()
def remove_gate():
	postdata = get_post_json_data()
	sn = postdata['sn']
	for s in sn:
		doc = frappe.get_doc("IOT Device", s)
		doc.update_owner("", None)
	return True


@frappe.whitelist()
def update_gate(sn, name, desc):
	doc = frappe.get_doc("IOT Device", sn)
	doc.update({
		"dev_name": name,
		"description": desc
	})
	doc.save()
	return True


@frappe.whitelist(allow_guest=True)
def gate_info(sn):
	valid_auth_code()
	device = frappe.get_doc('IOT Device', sn)
	if not device.has_permission("read"):
		raise frappe.PermissionError
	basic = {
		'sn': device.sn,
		'model': "Q102",
		'name': device.dev_name,
		'desc': device.description,
		'company': device.company,
		'location': device.sn,
		'beta': device.use_beta,
		'iot_beta': gate_is_beta(sn),
		'status': device.device_status,
	}
	config = {}
	applist = {}
	client_11 = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/11")
	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/12")
	if client.exists(sn):
		info = client.hgetall(sn)
		if info:
			config['iot_version'] = eval(info.get("version/value"))[1]
			config['skynet_version'] = eval(info.get("skynet_version/value"))[1]
			_starttime = eval(info.get("starttime/value"))[1]
			config['starttime'] = str(
				convert_utc_to_user_timezone(datetime.datetime.utcfromtimestamp(int(_starttime))).replace(
					tzinfo=None))
			config['uptime'] = int(eval(info.get("uptime/value"))[1] / 1000)
			print(info.get("skynet_platform/value"))
			config['platform'] = eval(info.get("platform/value"))[1]
			config['data_upload'] = eval(info.get("data_upload/value"))[1]
			config['data_upload_period'] = eval(info.get("data_upload_period/value"))[1]
			config['data_upload_cov'] = eval(info.get("data_upload/value"))[1]
			config['data_upload_cov_ttl'] = eval(info.get("data_upload_period/value"))[1]
			config['stat_upload'] = eval(info.get("data_upload/value"))[1]

		try:
			s = requests.Session()
			s.auth = ("api", "Pa88word")
			r = s.get('http://127.0.0.1:18083/api/v2/nodes/emq@127.0.0.1/clients/' + sn)
			rdict = json.loads(r.text)
			if rdict and rdict['result']:
				objects = rdict['result']['objects']
				if (len(objects) > 0):
					config['public_ip'] = rdict['result']['objects'][0]['ipaddress']
					config['public_port'] = rdict['result']['objects'][0]['port']
		except Exception as ex:
			frappe.logger(__name__).error(ex)

		config['cpu'] = "imx6ull 528MHz"
		config['ram'] = "256 MB"
		config['rom'] = "4 GB"
		config['os'] = "openwrt"
	try:
		client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/6")
		applist = json.loads(client.get(sn))
	except Exception as ex:
		applist = {}

	return {
		'basic': basic,
		'config': config,
		'applist': applist,
		"devs_len": client_11.llen(sn),
		"apps_len": len(applist)
	}


@frappe.whitelist(allow_guest=True)
def gate_applist(sn):
	valid_auth_code()
	device = frappe.get_doc('IOT Device', sn)
	if not device.has_permission("read"):
		raise frappe.PermissionError

	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/6")
	applist = json.loads(client.get(sn) or "[]")

	iot_applist = []
	for app in applist:
		app_obj = frappe._dict(applist[app])
		try:
			applist[app]['inst'] = app
			from iot.hdb import iot_device_tree as _iot_device_tree
			from iot.hdb import iot_device_cfg as _iot_device_cfg
			device_tree = _iot_device_tree(sn)
			devs_len = 0
			for devsn in device_tree:
				cfg = _iot_device_cfg(sn, devsn)
				if cfg['meta']['app'] == app:
					devs_len = devs_len + 1
			applist[app]['devs_len'] = devs_len
			if not frappe.get_value("IOT Application", app_obj.name, "name"):
				iot_applist.append({
					"cloud": None,
					"info": applist[app],
					"inst": app,
				})
				continue
			else:
				doc = frappe.get_doc("IOT Application", app_obj.name)
				if app_obj.auto is None:
					applist[app]['auto'] = "1"

				iot_applist.append({
					"cloud": {
						"name": doc.name,
						"app_name": doc.app_name,
						"owner": doc.owner,
						"fullname": get_fullname(doc.owner),
						"ver": get_latest_version(doc.name, device.use_beta),
						"fork_app": doc.fork_from,
						"fork_ver": doc.fork_version,
						"icon_image": doc.icon_image,
					},
					"info": applist[app],
					"inst": app,
				})
		except Exception as ex:
			frappe.logger(__name__).error(ex)
	return iot_applist


@frappe.whitelist(allow_guest=True)
def gate_app_detail(sn, inst=None):
	valid_auth_code()
	device = frappe.get_doc('IOT Device', sn)
	if not device.has_permission("read"):
		raise frappe.PermissionError
	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/6")
	applist = json.loads(client.get(sn) or "[]")
	for app in applist:
		if app==inst:
			app_obj = frappe._dict(applist[app])
			try:
				applist[app]['inst'] = app
				if not frappe.get_value("IOT Application", app_obj.name, "name"):
					if app_obj.auto is None:
						applist[app]['auto'] = "1"
					return {"cloud": None, "info": applist[app], "inst": app}
				else:
					doc = frappe.get_doc("IOT Application", app_obj.name)
					if app_obj.auto is None:
						applist[app]['auto'] = "1"
					return {"cloud": {
							"name": doc.name,
							"app_name": doc.app_name,
							"owner": doc.owner,
							"fullname": get_fullname(doc.owner),
							"ver": get_latest_version(doc.name, device.use_beta),
							"fork_app": doc.fork_from,
							"fork_ver": doc.fork_version,
							"icon_image": doc.icon_image,
							},
							"info": applist[app],
							"inst": app,
						}
			except Exception as ex:
				frappe.logger(__name__).error(ex)
	return None

@frappe.whitelist(allow_guest=True)
def gate_app_dev_tree(sn):
	valid_auth_code()
	from iot.hdb import iot_device_tree as _iot_device_tree
	from iot.hdb import iot_device_cfg as _iot_device_cfg

	device_tree = _iot_device_tree(sn)
	app_dev_tree = frappe._dict({})

	for devsn in device_tree:
		cfg = _iot_device_cfg(sn, devsn)
		devmeta = cfg['meta']
		if not devmeta:
			continue

		app = devmeta['app']
		if not app:
			continue

		devmeta['sn']=devsn
		if not app_dev_tree.get(app):
			app_dev_tree[app] = []
		app_dev_tree[app].append(devmeta)

	return app_dev_tree


@frappe.whitelist(allow_guest=True)
def gate_devs_list(sn):
	valid_auth_code()
	from iot.hdb import iot_device_tree as _iot_device_tree
	from iot.hdb import iot_device_cfg as _iot_device_cfg

	device_tree = _iot_device_tree(sn)
	app_devs_list = []

	for devsn in device_tree:
		cfg = _iot_device_cfg(sn, devsn)
		if cfg.has_key('meta'):
			devmeta = cfg['meta']
			devmeta['sn'] = devsn
			if cfg.has_key('inputs'):
				devmeta['inputs'] = len(cfg['inputs'])
			if cfg.has_key('outputs'):
				devmeta['outputs'] = len(cfg['outputs'])
			if cfg.has_key('commands'):
				devmeta['commands'] = len(cfg['commands'])
			app_devs_list.append(devmeta)

	return app_devs_list

@frappe.whitelist(allow_guest=True)
def gate_device_data_array(sn=None, vsn=None):
	valid_auth_code()
	from iot.hdb import iot_device_data_array
	return iot_device_data_array(sn, vsn)


UTC_FORMAT1 = "%Y-%m-%dT%H:%M:%S.%fZ"
UTC_FORMAT2 = "%Y-%m-%dT%H:%M:%SZ"


def utc2local(utc_st):
	now_stamp = time.time()
	local_time = datetime.datetime.fromtimestamp(now_stamp)
	utc_time = datetime.datetime.utcfromtimestamp(now_stamp)
	offset = local_time - utc_time
	local_st = utc_st + offset
	return local_st


@frappe.whitelist(allow_guest=True)
def taghisdata(sn, vsn=None, vt=None, tag=None, time_condition=None, value_method=None, group_time_span=None, fill_method=None, count_limit=None, time_zone=None):
	valid_auth_code()
	import HTMLParser
	html_parser = HTMLParser.HTMLParser()
	vsn = vsn or sn
	doc = frappe.get_doc('IOT Device', sn)
	if not doc.has_permission("read"):
		raise frappe.PermissionError

	inf_server = IOTHDBSettings.get_influxdb_server()
	if not inf_server:
		frappe.logger(__name__).error("InfluxDB Configuration missing in IOTHDBSettings")
		return

	# ------------------------------------------------------------------------------------------------------------------
	vtdict = {"float": "value", "int": "int_value", "string": "string_value"}
	vt = vt or "float"
	field = '"' + vtdict.get(vt) + '"'
	fields = '"' + vtdict.get(vt) + '"' + ' , "quality"'
	method = dict(raw=fields, mean='mean("' + field + '")', max='max("' + field + '")', min='min("' + field + '")', first='first("' + field + '")',
	              last='last("' + field + '")', sum='sum("' + field + '")', count='count("' + field + '")')
	if value_method not in ["raw", "mean", "max", "min", "first", "last", "sum", "count"]:
		value_method = "raw"
	filter = ' "iot"=\'' + sn + '\' AND "device"=\'' + vsn + '\''
	if value_method != "raw":
		filter = ' "iot"=\'' + sn + '\' AND "device"=\'' + vsn + '\'' + ' AND "quality"=0 '
	group_time_span = group_time_span or "1m"
	# fill_method = "null/previous/none/linear"
	time_condition = time_condition or 'time > now() - 10m'
	time_condition = html_parser.unescape(time_condition)
	fill_method = fill_method or "none"
	group_method = ' GROUP BY time(' + group_time_span + ') FILL(' + fill_method + ')'
	count = count_limit or 200
	time_zone = time_zone or 'Asia/Shanghai'

	query = 'SELECT'
	get_method = method["raw"]
	if value_method:
		get_method = method[value_method]
	query = query + ' ' + get_method + ' FROM "' + tag + '"' + ' WHERE ' + filter + ' AND ' + time_condition
	if value_method != "raw":
		query = query + group_method
	query = query + ' limit ' + str(count) + " tz('" + time_zone + "')"
	# print("+++++++++++++++++++++++++++++++++++++++++++++++++", query)
	# ------------------------------------------------------------------------------------------------------------------
	domain = frappe.get_value("Cloud Company", doc.company, "domain")
	r = requests.session().get(inf_server + "/query", params={"q": query, "db": domain}, timeout=10)
	# print("@@@@@@@@@@@@", r)
	if r.status_code == 200:
		ret = r.json()
		# print(ret)
		if not ret:
			return
		results = ret['results']
		if not results or len(results) < 1:
			return
		series = results[0].get('series')
		if not series or len(series) < 1:
			return
		res = series[0].get('values')
		if not res:
			return
		taghis = []
		# print('@@@@@@@@@@@@@@@@@', len(res))
		if value_method == "raw":
			for i in range(0, len(res)):
				hisvalue = {'name': tag, 'value': res[i][1], 'time': res[i][0], 'quality': res[i][2], 'vsn': vsn}
				taghis.append(hisvalue)
		else:
			for i in range(0, len(res)):
				hisvalue = {'name': tag, 'value': res[i][1], 'time': res[i][0], 'quality': 0, 'vsn': vsn}
				taghis.append(hisvalue)
		return taghis


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
	return apps


@frappe.whitelist()
def appstore_category():
	return frappe.get_all("App Category", fields=["name", "description"])


@frappe.whitelist()
def appstore_supplier():
	return frappe.get_all("App Device Supplier", fields=["name", "description"])


@frappe.whitelist()
def appstore_protocol():
	return frappe.get_all("App Device Protocol", fields=["name", "description"])


@frappe.whitelist()
def app_details(app_name):
	return frappe.get_doc('IOT Application', app_name)


@frappe.whitelist(allow_guest=True)
def app_review(app):
	filters = {"app": app}
	return frappe.get_all('IOT Application Review', "*", filters, order_by="modified desc")


@frappe.whitelist()
def query_device_activity():
	from iot.iot.doctype.iot_device_activity.iot_device_activity import query_logs_by_user as _query_logs_by_user
	return _query_logs_by_user(frappe.session.user)


@frappe.whitelist()
def query_device_activity_by_company():
	from iot.iot.doctype.iot_device_activity.iot_device_activity import query_logs_by_company as _query_logs_by_company
	company = frappe.get_value("Cloud Employee", frappe.session.user, "company")
	if not company:
		return None
	return _query_logs_by_company(company)


@frappe.whitelist()
def query_firmware_lastver(sn, beta):
	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/12")
	if client.exists(sn):
		info = client.hgetall(sn)
		if info:
			gate_platform = eval(info.get("platform/value"))[1]
			firmware_lastver = get_latest_version(gate_platform+"_skynet", int(beta))
			freeioe_lastver = get_latest_version("freeioe", int(beta))
			return {"firmware_lastver": firmware_lastver, "freeioe_lastver": freeioe_lastver}
	return None


@frappe.whitelist()
def device_status_statistics():
	company = frappe.get_value('Cloud Employee', frappe.session.user, 'company')
	if not company:
		return

	inf_server = IOTHDBSettings.get_influxdb_server()
	if not inf_server:
		frappe.logger(__name__).error("InfluxDB Configuration missing in IOTHDBSettings")
		return

	query = 'SELECT "online", "offline" FROM "device_status_statistics" WHERE time > now() - 12h AND "owner"=\'' + company + '\''
	domain = frappe.get_value("Cloud Company", company, "domain")
	r = requests.session().get(inf_server + "/query", params={"q": query, "db": domain + '.statistics'}, timeout=10)
	if r.status_code == 200:
		ret = r.json()
		if not ret:
			return

		results = ret['results']
		if not results or len(results) < 1:
			return

		series = results[0].get('series')
		if not series or len(series) < 1:
			return

		res = series[0].get('values')
		if not res:
			return

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
			local_time = str(convert_utc_to_user_timezone(utc_time).replace(tzinfo=None))
			hisvalue = {'name': 'device_status_statistics', 'online': res[i][1], 'time': local_time, 'offline': res[i][2], 'owner': company}
			taghis.append(hisvalue)
		return taghis


@frappe.whitelist()
def device_event_type_statistics():
	company = frappe.get_value('Cloud Employee', frappe.session.user, 'company')
	if not company:
		return

	inf_server = IOTHDBSettings.get_influxdb_server()
	if not inf_server:
		frappe.logger(__name__).error("InfluxDB Configuration missing in IOTHDBSettings")
		return

	query = 'SELECT sum("系统") AS "系统", sum("设备") AS "设备", sum("通讯") AS "通讯", sum("数据") AS "数据", sum("应用") AS "应用"'
	query = query + ' FROM "device_event_type_statistics" WHERE time > now() - 7d'
	query = query + ' AND "owner"=\'' + company + '\' GROUP BY time(1d) FILL(0)'
	domain = frappe.get_value("Cloud Company", company, "domain")
	r = requests.session().get(inf_server + "/query", params={"q": query, "db": domain + '.statistics'}, timeout=10)
	if r.status_code == 200:
		ret = r.json()
		if not ret:
			return

		results = ret['results']
		if not results or len(results) < 1:
			return

		series = results[0].get('series')
		if not series or len(series) < 1:
			return

		res = series[0].get('values')
		if not res:
			return

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
			local_time = str(convert_utc_to_user_timezone(utc_time).replace(tzinfo=None))
			hisvalue = {'name': 'device_event_type_statistics', 'time': local_time, 'owner': company}
			hisvalue['系统'] = res[i][1] or 0
			hisvalue['设备'] = res[i][2] or 0
			hisvalue['通讯'] = res[i][3] or 0
			hisvalue['数据'] = res[i][4] or 0
			hisvalue['应用'] = res[i][5] or 0
			taghis.append(hisvalue)
		return taghis


@frappe.whitelist()
def device_event_count_statistics():
	company = frappe.get_value('Cloud Employee', frappe.session.user, 'company')
	if not company:
		return

	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/15")

	from iot.hdb_api import list_iot_devices as _list_iot_devices
	devices = _list_iot_devices(frappe.session.user)
	company_devices = devices.get('company_devices')

	try:
		result = []
		if company_devices:
			for group in company_devices:
				devices = group["devices"]
				for dev in devices:
					devdoc = IOTDevice.get_device_doc(dev)
					if devdoc:
						vals = client.hgetall('event_count.' + dev)
						vals['sn'] = dev
						vals['name'] = devdoc.dev_name
						vals['last_updated'] = str(devdoc.last_updated)[:-7]
						vals['position'] = 'N/A'
						vals['device_status'] = devdoc.device_status
						result.append(vals)

		return result
	except Exception as ex:
		return []


@frappe.whitelist()
def device_type_statistics():
	company = frappe.get_value('Cloud Employee', frappe.session.user, 'company')
	if not company:
		return

	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/15")
	try:
		return client.hgetall('device_type.' + company)
	except Exception as ex:
		return []


@frappe.whitelist()
def apply_AccessKey():
	AccessKey = frappe.db.get_value("IOT User Api", frappe.session.user, "authorization_code")
	if AccessKey:
		return AccessKey
	else:
		new_token = str(uuid.uuid1()).lower()
		doc = frappe.get_doc({
			"doctype": "IOT User Api",
			"user": frappe.session.user,
			"authorization_code": new_token
		}).insert()
		return new_token


@frappe.whitelist()
def renew_AccessKey():
	AccessKey = frappe.db.get_value("IOT User Api", frappe.session.user, "authorization_code")
	if AccessKey:
		doc = frappe.get_doc("IOT User Api", frappe.session.user)
		new_token = str(uuid.uuid1()).lower()
		doc.set("authorization_code", new_token)
		if doc.user == frappe.session.user:
			doc.save(ignore_permissions=True)
		else:
			doc.save()
		return new_token
	else:
		throw(_("Your Account has no authorization_code"))

@frappe.whitelist()
def delete_AccessKey():
	frappe.delete_doc("IOT User Api", frappe.session.user, ignore_permissions=True)
	return True


@frappe.whitelist()
def get_virtual_gates():
	virtual_gates = [d[0] for d in frappe.db.get_values('IOT Virtual Device', {"user": frappe.session.user})]
	# virtual_gates = [d.name for d in frappe.get_all('IOT Virtual Device', {"user": frappe.session.user})]
	return virtual_gates


@frappe.whitelist()
def apply_version_publish(appid, version):
	appdoc = frappe.get_doc("IOT Application Version", appid + "." + str(version))
	if appdoc:
		if appdoc.beta:
			appdoc.set("beta", 0)
			appdoc.save(ignore_permissions=True)
		return {"appid": appid, "version": version, "beta": appdoc.beta}


@frappe.whitelist(allow_guest=True)
def gate_applist_detail(sn):
	valid_auth_code()
	device = frappe.get_doc('IOT Device', sn)
	if not device.has_permission("read"):
		raise frappe.PermissionError

	from iot.hdb import iot_device_tree as _iot_device_tree
	from iot.hdb import iot_device_cfg as _iot_device_cfg
	device_tree = _iot_device_tree(sn)


	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/6")
	applist = json.loads(client.get(sn) or "[]")

	iot_applist = []
	for app in applist:
		app_obj = frappe._dict(applist[app])
		try:
			applist[app]['inst'] = app
			devs = []
			for devsn in device_tree:
				cfg = _iot_device_cfg(sn, devsn)
				if cfg['meta']['app'] == app:
					devs.append(devsn)
					pass
			if not frappe.get_value("IOT Application", app_obj.name, "name"):
				iot_applist.append({
					"cloud": None,
					"info": applist[app],
					"inst": app,
					"devs": len(devs)
				})
				continue
			else:
				doc = frappe.get_doc("IOT Application", app_obj.name)
				if app_obj.auto is None:
					applist[app]['auto'] = "1"

				iot_applist.append({
					"cloud": {
						"name": doc.name,
						"app_name": doc.app_name,
						"owner": doc.owner,
						"fullname": get_fullname(doc.owner),
						"ver": get_latest_version(doc.name, device.use_beta),
						"fork_app": doc.fork_from,
						"fork_ver": doc.fork_version,
						"icon_image": doc.icon_image,
					},
					"info": applist[app],
					"inst": app,
					"devs": len(devs)
				})

		except Exception as ex:
			frappe.logger(__name__).error(ex)
	return iot_applist

