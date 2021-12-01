# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, nowdate, cint
from frappe import utils
from erpnext.setup.doctype.item_group.item_group import get_item_for_list_in_html
from erpnext.shopping_cart.product_info import set_product_info_for_website
import datetime
from datetime import date
from frappe.utils.password import update_password as _update_password
from frappe.utils.data import flt, nowdate, getdate, cint
from frappe.utils import cint, cstr, flt, nowdate, comma_and, date_diff, getdate , add_days, add_years
from pypaytabs import Paytabs
from pypaytabs import Utilities as util
import requests 
from frappeclient import FrappeClient


@frappe.whitelist(allow_guest=True)
def get_invoice_details(invoice):
	# conn = FrappeClient("https://demo.pas.sa")
	# conn.login("administrator", "LkOqnVQapzRZWMd")

	# doc = conn.get_doc('Sales Invoice', invoice)

	doc = frappe.get_doc('Sales Invoice', invoice)

	return doc.return_against, doc.posting_date, ':'.join(str(doc.posting_time).split(':')[:2])

