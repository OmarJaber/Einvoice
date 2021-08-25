# encoding=utf8
# -*- coding: utf-8 -*- u
from __future__ import unicode_literals
from __future__ import division
import frappe
import frappe, os , math
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_site_base_path, cint, cstr, date_diff, flt, formatdate, getdate, get_link_to_form, \
    comma_or, get_fullname, add_years, add_months, add_days, nowdate
from frappe.utils.data import flt, nowdate, getdate, cint, rounded, add_months, add_days, get_last_day
from frappe.utils.csvutils import read_csv_content_from_uploaded_file
from frappe.utils.password import update_password as _update_password
from frappe.utils import cint, cstr, flt, nowdate, comma_and, date_diff, getdate, formatdate
# from umalqurra.hijri_date import HijriDate
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from erpnext.hr.doctype.salary_slip.salary_slip import SalarySlip
from erpnext.hr.doctype.leave_application.leave_application import get_leaves_for_period
from erpnext.hr.doctype.leave_application.leave_application import get_leave_allocation_records
from frappe.model.mapper import get_mapped_doc
import sys
from frappe.core.doctype.sms_settings.sms_settings import send_sms
from frappe.utils.file_manager import upload
from frappeclient import FrappeClient
from frappe.utils.print_format import download_pdf


@frappe.whitelist()
def download_sales_invoice(sales_invoice):
    if not frappe.db.exists("Sales Invoice", {"name": sales_invoice}):
        return "Selected Sales Invoice is not exists"
    else:
        doc = frappe.get_doc("Sales Invoice", sales_invoice)

        return download_pdf(doc.doctype, doc.name, format='Standard', doc=doc)
         



@frappe.whitelist()
def send_sales_invoice_via_email(sales_invoice):
    if not frappe.db.exists("Sales Invoice", {"name": sales_invoice}):
        return "Selected Sales Invoice is not exists"
    else:
        doc = frappe.get_doc("Sales Invoice", sales_invoice)

        msg = frappe.render_template('einvoice/templates/emails/invoice.html', context={"sales_invoice": doc})

        sender = frappe.get_value("Email Account", filters = {"default_outgoing": 1}, fieldname = "email_id") or None
        recipient = doc.email

        attachments = [frappe.attach_print("Sales Invoice", doc.name, print_format='Standard')]

        frappe.sendmail(
            sender=sender,
            recipients= recipient,
            content=msg,
            subject="Invoice {0}".format(doc.name),
            delayed=False,
            reference_doctype=doc.doctype,
            reference_name=doc.name,
            attachments=attachments
        )

        return "Email Sent Successfully"




@frappe.whitelist()
def import_profil_image(cmd, doctype, docname, filename, filedata, from_form):
    url = "https://far.erptag.com/api/method/uploadfile"
    payload = {
            'cmd': cmd, 
            'doctype': doctype,
            'docname': docname,
            'filename': filename,
            'filedata' : filedata,
            'from_form' : from_form
        }
    headers = {"Content-type": "multipart/form-data"}
    res = requests.post(url,data = json.dumps(payload), headers=headers)
    
    return res.json()


