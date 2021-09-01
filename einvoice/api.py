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
def download_all_filtered_sales_invoice(from_date, to_date):

    invoices_sql = []

    doc = frappe.new_doc("Download Sales Invoice")
    
    invoices = frappe.db.sql_list("select name from `tabSales Invoice` where posting_date between '{0}' and '{1}' order by posting_date".format(from_date, to_date))
    for invoice in invoices:
        sales_invoice_doc=frappe.get_doc("Sales Invoice", invoice)
        invoices_sql.append(invoice)
        doc.append('invoices',{
            "sales_invoice": invoice,
            "posting_date": sales_invoice_doc.posting_date,
            "total_amount": sales_invoice_doc.grand_total
        })
    
    invoices_sql = tuple(invoices_sql)

    taxes = frappe.db.sql("select taxes, sum(tax_value) from `tabSales Taxes and Charges` where parent in {0} group by taxes".format(invoices_sql))
    for taxe in taxes:
        doc.append('taxes',{
            "taxes": taxe[0],
            "tax_value": taxe[1]
        })
        
    total = frappe.db.sql("select sum(total_without_tax), sum(total_tax_amount), sum(grand_total) from `tabSales Invoice` where posting_date between '{0}' and '{1}' order by posting_date".format(from_date, to_date))

    doc.total_without_tax = total[0][0]
    doc.total_tax_amount = total[0][1]
    doc.grand_total = total[0][2]

    doc.save(ignore_permissions=True)

    result = download_pdf(doc.doctype, doc.name, format='New Standard', doc=doc)

    doc.delete()
    
    return result





@frappe.whitelist()
def get_specific_filtered_sales_invoice(from_date, to_date, current_page_number, page_entries):
    current_page_number = int(current_page_number)
    page_entries = int(page_entries)

    invoices_sql = []
    data = {
      "invoices": [],
      "taxes": [],
      "number_of_pages": 0,
      "current_page_number": 1,
      "page_entries": 10,
      "total_without_tax": 0,
      "total_tax_amount": 0,
      "grand_total": 0
    }

    invoices = frappe.db.sql_list("select name from `tabSales Invoice` where posting_date between '{0}' and '{1}' order by posting_date".format(from_date, to_date))
    for invoice in invoices:
        doc=frappe.get_doc("Sales Invoice", invoice)
        data["invoices"].append({'name': invoice, 'posting_date': doc.posting_date, 'grand_total': doc.grand_total, 'total_tax_amount': doc.total_tax_amount})
        invoices_sql.append(invoice)

    invoices_sql = tuple(invoices_sql)
    
    taxes = frappe.db.sql("select taxes, sum(tax_value) from `tabSales Taxes and Charges` where parent in {0} group by taxes".format(invoices_sql))
    for taxe in taxes:
        data["taxes"].append({'Tax': taxe[0], 'tax_value': taxe[1]})


    number_of_pages = math.ceil(len(data["invoices"])/flt(page_entries))

    if current_page_number > number_of_pages:
        return "Page Number {0} is not exists".format(current_page_number)

    data.update({"number_of_pages": number_of_pages})
    data.update({"current_page_number": current_page_number})
    data.update({"page_entries": page_entries})


    total = frappe.db.sql("select sum(total_without_tax), sum(total_tax_amount), sum(grand_total) from `tabSales Invoice` where posting_date between '{0}' and '{1}' order by posting_date".format(from_date, to_date))

    data.update({"total_without_tax": total[0][0]})
    data.update({"total_tax_amount": total[0][1]})
    data.update({"grand_total": total[0][2]})

    
    new_array = list(chunks(data["invoices"], int(page_entries)))[current_page_number-1]
    
    data.update({"invoices": new_array})


    return data



def chunks(iterable, n):
    """assumes n is an integer>0
    """
    iterable=iter(iterable)
    while True:
        result=[]
        for i in range(n):
            try:
                a=next(iterable)
            except StopIteration:
                break
            else:
                result.append(a)
        if result:
            yield result
        else:
            break
         


@frappe.whitelist()
def get_all_filtered_sales_invoice(from_date, to_date):

    invoices_sql = []
    data = {
      "invoices": [],
      "taxes": [],
      "total_without_tax": 0,
      "total_tax_amount": 0,
      "grand_total": 0
    }

    invoices = frappe.db.sql_list("select name from `tabSales Invoice` where posting_date between '{0}' and '{1}' order by posting_date".format(from_date, to_date))
    for invoice in invoices:
        doc=frappe.get_doc("Sales Invoice", invoice)
        data["invoices"].append({'name': invoice, 'posting_date': doc.posting_date, 'grand_total': doc.grand_total, 'total_tax_amount': doc.total_tax_amount})
        invoices_sql.append(invoice)

    invoices_sql = tuple(invoices_sql)
    
    taxes = frappe.db.sql("select taxes, sum(tax_value) from `tabSales Taxes and Charges` where parent in {0} group by taxes".format(invoices_sql))
    for taxe in taxes:
        data["taxes"].append({'Tax': taxe[0], 'tax_value': taxe[1]})

        
    total = frappe.db.sql("select sum(total_without_tax), sum(total_tax_amount), sum(grand_total) from `tabSales Invoice` where posting_date between '{0}' and '{1}' order by posting_date".format(from_date, to_date))

    data.update({"total_without_tax": total[0][0]})
    data.update({"total_tax_amount": total[0][1]})
    data.update({"grand_total": total[0][2]})

    return data

         



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

        msg = frappe.render_template('einvoice/templates/emails/invoice_ar.html', context={"sales_invoice": doc})

        sender = frappe.get_value("Email Account", filters = {"default_outgoing": 1}, fieldname = "email_id") or None
        recipient = doc.email

        attachments = [frappe.attach_print("Sales Invoice", doc.name, print_format='New Standard SI AR')]

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


