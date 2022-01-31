// Copyright (c) 2021, Estores and contributors
// For license information, please see license.txt


frappe.ui.form.on('EInvoice Sales Invoice', {
	onload: function(frm) {

		frappe.call({
		    method: 'get_company_info',
		    doc: frm.doc,
		    callback: function(r) {
		        if (r.message) {
		            cur_frm.set_value("company_name", r.message[0]);
		            cur_frm.set_value("company_address", r.message[1]);
		            cur_frm.set_value("company_mobile", r.message[2]);
		            cur_frm.set_value("tax_id", r.message[3]);
		            cur_frm.set_value("commercial_registration_no", r.message[4]);
		        }
		    }
		});

	}
});


frappe.ui.form.on('EInvoice Sales Invoice Item', {
	item: function(frm, cdt, cdn){
		var d = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "qty", );
		frappe.model.set_value(cdt, cdn, "total", 0);
	},
	price: function(frm, cdt, cdn){
		var d = locals[cdt][cdn];
		if(d.price && d.qty) {
			frappe.model.set_value(cdt, cdn, "total", d.price*d.qty);
			frappe.model.set_value(cdt, cdn, "tax_value", (d.rate/100.0)*d.total);
			frappe.model.set_value(cdt, cdn, "amount", d.total+d.tax_value);

			var total = 0;
			var tax = 0;
	        $.each(frm.doc.items || [], function (i, d) {
	            total += d.total;
	            tax += d.tax_value;
	        });
	        cur_frm.set_value("total", total);
	        cur_frm.set_value("total_without_tax", total);
	        cur_frm.set_value("total_tax_amount", tax);
	        
	        cur_frm.set_value("grand_total", cur_frm.doc.total_without_tax+cur_frm.doc.total_tax_amount);

		}
	},
	qty: function(frm, cdt, cdn){
		var d = locals[cdt][cdn];
		if(d.price && d.qty) {
			frappe.model.set_value(cdt, cdn, "total", d.price*d.qty);
			frappe.model.set_value(cdt, cdn, "tax_value", (d.rate/100.0)*d.total);
			frappe.model.set_value(cdt, cdn, "amount", d.total+d.tax_value);

			var total = 0;
			var tax = 0;
	        $.each(frm.doc.items || [], function (i, d) {
	            total += d.total;
	            tax += d.tax_value;
	        });
	        cur_frm.set_value("total", total);
	        cur_frm.set_value("total_without_tax", total);
	        cur_frm.set_value("total_tax_amount", tax);
	        
	        cur_frm.set_value("grand_total", cur_frm.doc.total_without_tax+cur_frm.doc.total_tax_amount);

		}
	}
})


