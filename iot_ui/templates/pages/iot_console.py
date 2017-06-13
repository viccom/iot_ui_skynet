# coding=utf-8
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _
from frappe.utils.user import get_fullname_and_avatar


def get_context(context):
    if frappe.session.user == 'Guest':
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect
    context.no_cache = 1
    context.show_sidebar = True

    menulist = frappe.get_all("Menu List")
    n_list = []
    for m in menulist:
        dd = { }
        print("@@@@@@@@", m['name'].decode('utf-8'))
        dd['url'] = frappe.get_value("Menu List", m['name'], "url")
        dd['name'] = frappe.get_value("Menu List", m['name'], "menuname")
        dd['ico'] = frappe.get_value("Menu List", m['name'], "menuico")
        dd['id'] = frappe.get_value("Menu List", m['name'], "id")
        n_list.append(dd)

    n_list.sort(key=lambda k: (k.get('id', 0)))
    context.leftnavlist = n_list
    context.title = 'iot_console'