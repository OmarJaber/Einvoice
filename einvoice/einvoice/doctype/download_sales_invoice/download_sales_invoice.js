// Copyright (c) 2021, Omar and contributors
// For license information, please see license.txt

frappe.ui.form.on('Download Sales Invoice', {
	onload: function(frm) {
		frappe.call({
		    method: 'get_company_info',
		    doc: frm.doc,
		    callback: function(r) {
		        if (r.message) {
		            cur_frm.set_value("company_name", r.message[0]);
		            cur_frm.set_value("tax_id", r.message[1]);
		        }
		    }
		});

	}
});
