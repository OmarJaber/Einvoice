# -*- coding: utf-8 -*-
# Copyright (c) 2021, Estores and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cint, cstr, flt, nowdate, comma_and, date_diff, getdate

class SalesInvoice(Document):
	def validate(self):
		total = 0
		total_tax = 0
		for item in self.items:
			item.total_without_tax = flt(item.qty)*flt(item.price)
			item.tax = item.total_without_tax*(item.tax_rate/100)
			item.total_amount = item.total_without_tax+item.tax
			total = total+item.total_amount


		self.grand_total = total
