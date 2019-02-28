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


@frappe.whitelist(allow_guest=True)
def gate_wanip_his(sn, time_condition=None, count_limit=None, time_zone=None):
	valid_auth_code()
	import HTMLParser
	html_parser = HTMLParser.HTMLParser()
	doc = frappe.get_doc('IOT Device', sn)
	if not doc.has_permission("read"):
		raise frappe.PermissionError

	inf_server = IOTHDBSettings.get_influxdb_server()
	if not inf_server:
		frappe.logger(__name__).error("InfluxDB Configuration missing in IOTHDBSettings")
		return

	# ------------------------------------------------------------------------------------------------------------------
	tags = ["gate_status", "gate_wanip", "gate_fault", "gate_ipchange"]
	taghis = []
	fields = '"ipaddr"'
	filter = ' "iot"=\'' + sn + '\''
	time_condition = time_condition or 'time > now() - 7d'
	time_condition = html_parser.unescape(time_condition)
	count = count_limit or 200
	time_zone = time_zone or 'Asia/Shanghai'
	for tag in tags:
		query = 'SELECT ' + fields + ' FROM "' + tag + '"' + ' WHERE ' + filter + ' AND ' + time_condition + ' limit ' + str(count) + " tz('" + time_zone + "')"
		# print("+++++++++++++++++++++++++++++++++++++++++++++++++", query)
		# ------------------------------------------------------------------------------------------------------------------
		domain = "gates_trace"
		r = requests.session().get(inf_server + "/query", params={"q": query, "db": domain}, timeout=10)
		# print("@@@@@@@@@@@@", r)
		his = {}
		his[tag] = []
		if r.status_code == 200:
			ret = r.json()
			# print(ret)
			if not ret:
				taghis.append(his)
				continue
			results = ret['results']
			if not results or len(results) < 1:
				taghis.append(his)
				continue
			series = results[0].get('series')
			if not series or len(series) < 1:
				taghis.append(his)
				continue
			res = series[0].get('values')
			if not res:
				taghis.append(his)
				continue
			# print('@@@@@@@@@@@@@@@@@', len(res))
			for i in range(0, len(res)):
				hisvalue = {'value': res[i][1], 'time': res[i][0], 'sn': sn}
				his[tag].append(hisvalue)
		taghis.append(his)
	return taghis