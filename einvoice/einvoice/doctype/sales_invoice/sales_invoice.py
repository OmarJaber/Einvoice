# -*- coding: utf-8 -*-
# Copyright (c) 2021, Estores and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cint, cstr, flt, nowdate, comma_and, date_diff, getdate

class SalesInvoice(Document):
    def after_insert(self):
        for item_child in self.items:
            doc = frappe.get_doc("Item", item_child.item)
            doc.warehouse_quantity=int(doc.warehouse_quantity)-int(item.qty)
            doc.save(ignore_permissions=True)


    def before_insert(self):
        for item_child in self.items:
            doc = frappe.get_doc("Item", item_child.item)
            if int(item.qty)>int(doc.warehouse_quantity):
                frappe.throw("The requested quantity of item {0} is more than stock availability".format(item_child.item))
            elif int(doc.warehouse_quantity)==0:
                frappe.throw("The requested item {0} is out of stock".format(item_child.item))


    def validate(self):

        total = 0
        tax = 0
        for item in self.items:
            item.total = flt(item.qty)*flt(item.price)
            item.tax_value = (flt(item.rate)/100.0)*flt(item.total)
            item.amount = flt(item.total)+flt(item.tax_value)

            total = total+item.total
            tax = tax+item.tax_value
        
        
        self.total = total
        self.total_without_tax = total
        self.total_tax_amount = tax
        self.grand_total = self.total_without_tax+self.total_tax_amount


    def get_company_info(self):
        doc = frappe.get_single("Company Info")
        return doc.company_name, doc.address, doc.mobile, doc.tax_id


