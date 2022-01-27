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
import requests
from frappe.sessions import Session, clear_sessions, delete_session, get_sessions_to_clear


def create_qr_code(doc, method=None):
    import io
    import os
    from base64 import b64encode

    import frappe
    from frappe import _
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
    from frappe.utils.data import add_to_date, get_time, getdate
    from pyqrcode import create as qr_create
    from erpnext import get_region

    if not hasattr(doc, 'ksa_einv_qr'):
        create_custom_fields({
            doc.doctype: [
                dict(
                    fieldname='ksa_einv_qr',
                    label='KSA E-Invoicing QR',
                    fieldtype='Attach Image',
                    read_only=1, no_copy=1, hidden=1
                )
            ]
        })

    # Don't create QR Code if it already exists
    qr_code = doc.get("ksa_einv_qr")
    if qr_code and frappe.db.exists({"doctype": "File", "file_url": qr_code}):
        return

    meta = frappe.get_meta(doc.doctype)

    if "ksa_einv_qr" in [d.fieldname for d in meta.get_image_fields()]:
        ''' TLV conversion for
        1. Seller's Name
        2. VAT Number
        3. Time Stamp
        4. Invoice Amount
        5. VAT Amount
        '''
        tlv_array = []
        # Sellers Name
        seller_name = frappe.get_doc("Company Info").company_name

        if not seller_name:
            frappe.throw(_('Arabic name missing for {} in the company document').format(doc.company))

        tag = bytes([1]).hex()
        length = bytes([len(seller_name.encode('utf-8'))]).hex()
        value = seller_name.encode('utf-8').hex()
        tlv_array.append(''.join([tag, length, value]))

        # VAT Number
        tax_id = frappe.get_doc("Company Info").tax_id
        if not tax_id:
            frappe.throw(_('Tax ID missing for {} in the company document').format(doc.company))

        tag = bytes([2]).hex()
        length = bytes([len(tax_id)]).hex()
        value = tax_id.encode('utf-8').hex()
        tlv_array.append(''.join([tag, length, value]))

        # Time Stamp
        posting_date = getdate(doc.posting_date)
        time = get_time(doc.posting_time)
        seconds = time.hour * 60 * 60 + time.minute * 60 + time.second
        time_stamp = add_to_date(posting_date, seconds=seconds)
        time_stamp = time_stamp.strftime('%Y-%m-%dT%H:%M:%SZ')

        tag = bytes([3]).hex()
        length = bytes([len(time_stamp)]).hex()
        value = time_stamp.encode('utf-8').hex()
        tlv_array.append(''.join([tag, length, value]))

        # Invoice Amount
        invoice_amount = str(doc.grand_total)
        tag = bytes([4]).hex()
        length = bytes([len(invoice_amount)]).hex()
        value = invoice_amount.encode('utf-8').hex()
        tlv_array.append(''.join([tag, length, value]))

        # VAT Amount
        vat_amount = str(doc.total_tax_amount)

        tag = bytes([5]).hex()
        length = bytes([len(vat_amount)]).hex()
        value = vat_amount.encode('utf-8').hex()
        tlv_array.append(''.join([tag, length, value]))

        # Joining bytes into one
        tlv_buff = ''.join(tlv_array)

        # base64 conversion for QR Code
        base64_string = b64encode(bytes.fromhex(tlv_buff)).decode()

        qr_image = io.BytesIO()
        url = qr_create(base64_string, error='L')
        url.png(qr_image, scale=2, quiet_zone=1)

        name = frappe.generate_hash(doc.name, 5)

        # making file
        filename = f"QRCode-{name}.png".replace(os.path.sep, "__")
        _file = frappe.get_doc({
            "doctype": "File",
            "file_name": filename,
            "is_private": 0,
            "content": qr_image.getvalue(),
            "attached_to_doctype": doc.get("doctype"),
            "attached_to_name": doc.get("name"),
            "attached_to_field": "ksa_einv_qr"
        })

        _file.save()

        # assigning to document
        doc.db_set('ksa_einv_qr', _file.file_url)
        doc.notify_update()



@frappe.whitelist(allow_guest=True)
def print_invoice(sales_invoice):
    url = "{0}/printview?doctype=EInvoice%20Sales%20Invoice&name={1}&trigger_print=1&format=POS%20Invoice%20Arabic&no_letterhead=0&_lang=en".format(frappe.utils.get_url(), sales_invoice)
    return url



@frappe.whitelist(allow_guest=True)
def edit_item(**kwargs):
    kwargs=frappe._dict(kwargs)

    item_doc = frappe.get_doc("EInvoice Item", kwargs.item_name)
    if kwargs.item_name!=kwargs.item_new_name:
        item_doc.item_name = kwargs.item_new_name
    item_doc.item_group = kwargs.item_group
    item_doc.price = kwargs.price
    item_doc.warehouse_quantity = kwargs.warehouse_quantity
    item_doc.tax = kwargs.tax
    item_doc.img = kwargs.img
    item_doc.description = kwargs.description
    item_doc.save(ignore_permissions=True)

    if kwargs.item_name!=kwargs.item_new_name:
        import frappe.model.rename_doc as rd
        rd.rename_doc("EInvoice Item", kwargs.item_name, kwargs.item_new_name, force=True)

    return 'Done'



@frappe.whitelist(allow_guest=True)
def delete_item(item_name):
    doc = frappe.get_doc("EInvoice Item", item_name)
    doc.disabled=1
    doc.save(ignore_permissions=True)

    frappe.db.sql("update `tabEInvoice Item` set disabled=1 where item_name='{0}'".format(item_name))
    frappe.db.commit()
    
    return 'Done'

    

@frappe.whitelist(allow_guest=True)
def logging_out_user():
    for sid in frappe.db.sql_list("select sid from `tabSessions`"):
        delete_session(sid)
    return 'Done'
    


@frappe.whitelist()
def get_taxes():

    data = {
        "data": []
    }

    taxes = frappe.db.sql("select title, rate from `tabTaxes` order by rate")
    for tax in taxes:
        data["data"].append({'title': tax[0], 'rate': tax[1]})

    return data




@frappe.whitelist()
def item_search(search_key):

    data = {
        "data": []
    }

    items = frappe.db.sql("select item_name, item_group, price, warehouse_quantity, tax, rate, img, description from `tabEInvoice Item` where warehouse_quantity!=0 and disabled=0 and name like '%{0}%'or description like '%{0}%'".format(search_key))

    if len(items)==0:
        return "There are no product matches with the search key {0}".format(search_key)
    else: 
        for item in items:
            data["data"].append({'item_name': item[0], 'item_group': item[1], 'price': item[2], 'warehouse_quantity': item[3], 'tax': item[4], 'rate': item[5], 'img': item[6], 'description': item[7]})

        return data






@frappe.whitelist()
def check_existing(doctype, docname):
    if frappe.db.exists(doctype, {"name": docname}):
        return 1
    else:
        return 0




@frappe.whitelist()
def download_and_email_all_filtered_sales_invoice(from_date, to_date):

    invoices_sql = []

    doc = frappe.new_doc("Download Sales Invoice")
    
    invoices = frappe.db.sql_list("select name from `tabEInvoice Sales Invoice` where posting_date between '{0}' and '{1}' order by posting_date".format(from_date, to_date))
    for invoice in invoices:
        sales_invoice_doc=frappe.get_doc("EInvoice Sales Invoice", invoice)
        invoices_sql.append(invoice)
        doc.append('invoices',{
            "sales_invoice": invoice,
            "posting_date": sales_invoice_doc.posting_date,
            "total_without_tax": sales_invoice_doc.total_without_tax,
            "total_tax_amount": sales_invoice_doc.total_tax_amount,
            "grand_total": sales_invoice_doc.grand_total
        })
    
    invoices_sql = tuple(invoices_sql)

        
    total = frappe.db.sql("select sum(total_without_tax), sum(total_tax_amount), sum(grand_total) from `tabEInvoice Sales Invoice` where posting_date between '{0}' and '{1}' order by posting_date".format(from_date, to_date))

    doc.total_without_tax = total[0][0]
    doc.total_tax_amount = total[0][1]
    doc.grand_total = total[0][2]

    doc.save(ignore_permissions=True)

    result = download_pdf(doc.doctype, doc.name, format='New Standard', doc=doc)

    # doc.delete()
    

    company_info = frappe.get_doc("Company Info")
    if company_info.email_address and not company_info.stop_receiving_emails:
        msg = "<h3><b>In the attachment file, you will find all invoices between {0} and {1} period!</b></h3>".format(from_date, to_date)

        sender = frappe.get_value("Email Account", filters = {"default_outgoing": 1}, fieldname = "email_id") or None
        recipient = company_info.email_address

        attachments = [frappe.attach_print("Download Sales Invoice", doc.name, print_format='New Standard')]

        try:
            frappe.sendmail(
                sender=sender,
                recipients= recipient,
                content=msg,
                subject="Filtered Invoices {0}".format(doc.name),
                delayed=False,
                reference_doctype=doc.doctype,
                reference_name=doc.name,
                attachments=attachments
            )
        except Exception as e:
            return "يرجى إعداد حساب البريد إلكتروني أولا"


    return result









@frappe.whitelist()
def send_email_all_filtered_sales_invoice(from_date, to_date):

    invoices_sql = []

    doc = frappe.new_doc("Download Sales Invoice")
    
    invoices = frappe.db.sql_list("select name from `tabEInvoice Sales Invoice` where posting_date between '{0}' and '{1}' order by posting_date".format(from_date, to_date))
    for invoice in invoices:
        sales_invoice_doc=frappe.get_doc("EInvoice Sales Invoice", invoice)
        invoices_sql.append(invoice)
        doc.append('invoices',{
            "sales_invoice": invoice,
            "posting_date": sales_invoice_doc.posting_date,
            "total_without_tax": sales_invoice_doc.total_without_tax,
            "total_tax_amount": sales_invoice_doc.total_tax_amount,
            "grand_total": sales_invoice_doc.grand_total
        })
    
    invoices_sql = tuple(invoices_sql)

        
    total = frappe.db.sql("select sum(total_without_tax), sum(total_tax_amount), sum(grand_total) from `tabEInvoice Sales Invoice` where posting_date between '{0}' and '{1}' order by posting_date".format(from_date, to_date))

    doc.total_without_tax = total[0][0]
    doc.total_tax_amount = total[0][1]
    doc.grand_total = total[0][2]

    doc.save(ignore_permissions=True)

    # result = download_pdf(doc.doctype, doc.name, format='New Standard', doc=doc)

    # doc.delete()
    

    company_info = frappe.get_doc("Company Info")
    if company_info.email_address and not company_info.stop_receiving_emails:
        msg = "<h3><b>In the attachment file, you will find all invoices between {0} and {1} period!</b></h3>".format(from_date, to_date)

        sender = frappe.get_value("Email Account", filters = {"default_outgoing": 1}, fieldname = "email_id") or None
        recipient = company_info.email_address

        attachments = [frappe.attach_print("Download Sales Invoice", doc.name, print_format='New Standard')]

        try:
            frappe.sendmail(
                sender=sender,
                recipients= recipient,
                content=msg,
                subject="Filtered Invoices {0}".format(doc.name),
                delayed=False,
                reference_doctype=doc.doctype,
                reference_name=doc.name,
                attachments=attachments
            )
        except Exception as e:
            return "يرجى إعداد حساب البريد إلكتروني أولا"


        return "تم الارسال الى البريد الالكتروني"
    else:
        return "Please add your email to the company info page and enable receiving emails option!"





@frappe.whitelist()
def get_specific_filtered_sales_invoice(from_date, to_date, current_page_number, page_entries):
    current_page_number = int(current_page_number)
    page_entries = int(page_entries)

    invoices_sql = []
    data = {
      "invoices": [],
      "number_of_pages": 0,
      "current_page_number": 1,
      "page_entries": 10,
      "total_without_tax": 0,
      "total_tax_amount": 0,
      "grand_total": 0
    }

    invoices = frappe.db.sql_list("select name from `tabEInvoice Sales Invoice` where posting_date between '{0}' and '{1}' order by posting_date desc".format(from_date, to_date))
    for invoice in invoices:
        doc=frappe.get_doc("EInvoice Sales Invoice", invoice)
        data["invoices"].append({'name': invoice, 'posting_date': doc.posting_date, 'grand_total': doc.grand_total})
        invoices_sql.append(invoice)

    invoices_sql = tuple(invoices_sql)
    

    number_of_pages = math.ceil(len(data["invoices"])/flt(page_entries))

    if current_page_number > number_of_pages:
        return "Page Number {0} is not exists".format(current_page_number)

    data.update({"number_of_pages": number_of_pages})
    data.update({"current_page_number": current_page_number})
    data.update({"page_entries": page_entries})


    total = frappe.db.sql("select sum(total_without_tax), sum(total_tax_amount), sum(grand_total) from `tabEInvoice Sales Invoice` where posting_date between '{0}' and '{1}' order by posting_date desc".format(from_date, to_date))

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
      "total_without_tax": 0,
      "total_tax_amount": 0,
      "grand_total": 0
    }

    invoices = frappe.db.sql_list("select name from `tabEInvoice Sales Invoice` where posting_date between '{0}' and '{1}' order by posting_date".format(from_date, to_date))
    for invoice in invoices:
        doc=frappe.get_doc("EInvoice Sales Invoice", invoice)
        data["invoices"].append({'name': invoice, 'posting_date': doc.posting_date, 'grand_total': doc.grand_total})
        invoices_sql.append(invoice)

    invoices_sql = tuple(invoices_sql)

        
    total = frappe.db.sql("select sum(total_without_tax), sum(total_tax_amount), sum(grand_total) from `tabEInvoice Sales Invoice` where posting_date between '{0}' and '{1}' order by posting_date".format(from_date, to_date))

    data.update({"total_without_tax": total[0][0]})
    data.update({"total_tax_amount": total[0][1]})
    data.update({"grand_total": total[0][2]})

    return data





@frappe.whitelist()
def download_sales_invoice(sales_invoice):
    if not frappe.db.exists("EInvoice Sales Invoice", {"name": sales_invoice}):
        return "Selected Sales Invoice is not exists"
    else:
        doc = frappe.get_doc("EInvoice Sales Invoice", sales_invoice)

        return download_pdf(doc.doctype, doc.name, format='POS Invoice Arabic', doc=doc)







@frappe.whitelist()
def send_sales_invoice_via_email(sales_invoice):
    company_info = frappe.get_doc("Company Info")
    if company_info.email_address and not company_info.stop_receiving_emails:
        if not frappe.db.exists("EInvoice Sales Invoice", {"name": sales_invoice}):
            return "Selected Sales Invoice is not exists"
        else:
            doc = frappe.get_doc("EInvoice Sales Invoice", sales_invoice)

            msg = frappe.render_template('einvoice/templates/emails/invoice_ar.html', context={"sales_invoice": doc, "company_info": company_info})

            sender = frappe.get_value("Email Account", filters = {"default_outgoing": 1}, fieldname = "email_id") or None
            recipient = company_info.email_address

            attachments = [frappe.attach_print("EInvoice Sales Invoice", doc.name, print_format='POS Invoice A4')]

            try:
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
            except Exception as e:
                return "يرجى إعداد حساب البريد إلكتروني أولا"
            

    
    doc = frappe.get_doc("EInvoice Sales Invoice", sales_invoice)
    
    msg = frappe.render_template('einvoice/templates/emails/invoice_ar.html', context={"sales_invoice": doc, "company_info": company_info})

    sender = frappe.get_value("Email Account", filters = {"default_outgoing": 1}, fieldname = "email_id") or None
    recipient = doc.email

    attachments = [frappe.attach_print("EInvoice Sales Invoice", doc.name, print_format='POS Invoice A4')]

    try:
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
    except Exception as e:
        return "يرجى إعداد حساب البريد إلكتروني أولا"
    
    return "تم الارسال الى البريد الالكتروني"





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


