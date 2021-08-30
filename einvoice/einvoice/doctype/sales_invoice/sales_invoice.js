// Copyright (c) 2021, Estores and contributors
// For license information, please see license.txt


frappe.ui.form.on('Sales Invoice', {
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

	},
	total: function(frm) {
		cur_frm.set_value("taxes", );
	}
});


frappe.ui.form.on('Sales Invoice Item', {
	price: function(frm, cdt, cdn){
		var d = locals[cdt][cdn];
		if(d.price && d.qty) {
			frappe.model.set_value(cdt, cdn, "amount", d.price*d.qty);

			var total = 0;
	        $.each(frm.doc.items || [], function (i, d) {
	            total += d.amount;
	        });
	        cur_frm.set_value("total", total);
	        cur_frm.set_value("total_without_tax", total);

	        cur_frm.set_value("grand_total", cur_frm.doc.total_without_tax+cur_frm.doc.total_tax_amount);

		}
	},
	qty: function(frm, cdt, cdn){
		var d = locals[cdt][cdn];
		if(d.price && d.qty) {
			frappe.model.set_value(cdt, cdn, "amount", d.price*d.qty);

			var total = 0;
	        $.each(frm.doc.items || [], function (i, d) {
	            total += d.amount;
	        });
	        cur_frm.set_value("total", total);
	        cur_frm.set_value("total_without_tax", total);

	        cur_frm.set_value("grand_total", cur_frm.doc.total_without_tax+cur_frm.doc.total_tax_amount);

		}
	}
})





frappe.ui.form.on('Sales Taxes and Charges', {
	taxes: function(frm, cdt, cdn){
		var d = locals[cdt][cdn];
		if(cur_frm.doc.total) {
			frappe.model.set_value(cdt, cdn, "total_amount", cur_frm.doc.total);
			frappe.model.set_value(cdt, cdn, "tax_value", (d.rate/100)*cur_frm.doc.total);

			var total = 0;
	        $.each(frm.doc.taxes || [], function (i, d) {
	            total += d.tax_value;
	        });
	        cur_frm.set_value("total_tax_amount", total);

	        cur_frm.set_value("grand_total", cur_frm.doc.total_without_tax+cur_frm.doc.total_tax_amount);

		}
	}
})



