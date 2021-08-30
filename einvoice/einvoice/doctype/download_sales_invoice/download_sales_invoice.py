# -*- coding: utf-8 -*-
# Copyright (c) 2021, Omar and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class DownloadSalesInvoice(Document):
	def get_company_info(self):
		doc = frappe.get_single("Company Info")
		return doc.company_name, doc.tax_id

	def validate(self):
		doc = frappe.get_single("Company Info")
		self.company_name = doc.company_name
		self.tax_id = doc.tax_id
