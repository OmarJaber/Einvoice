// Copyright (c) 2021, Estores and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Invoice', {
	validate: function(frm) {

	}
});


frappe.ui.form.on('Sales Invoice Item', {
	price: function(frm, cdt, cdn){
		var d = locals[cdt][cdn];
		if(d.price && d.qty) {
			frappe.model.set_value(cdt, cdn, "total_without_tax", d.price*d.qty);
			frappe.model.set_value(cdt, cdn, "tax", d.total_without_tax*(d.tax_rate/100));
			frappe.model.set_value(cdt, cdn, "total_amount", d.total_without_tax+d.tax);

			var total = 0;
	        $.each(frm.doc.items || [], function (i, d) {
	            total += d.total_amount;
	        });
	        cur_frm.set_value("grand_total", total);

		}
	},
	qty: function(frm, cdt, cdn){
		var d = locals[cdt][cdn];
		if(d.price && d.qty) {
			frappe.model.set_value(cdt, cdn, "total_without_tax", d.price*d.qty);
			frappe.model.set_value(cdt, cdn, "tax", d.total_without_tax*(d.tax_rate/100));
			frappe.model.set_value(cdt, cdn, "total_amount", d.total_without_tax+d.tax);

			var total = 0;
	        $.each(frm.doc.items || [], function (i, d) {
	            total += d.total_amount;
	        });
	        cur_frm.set_value("grand_total", total);

		}
	},
	item: function(frm, cdt, cdn){
		var d = locals[cdt][cdn];
		if(d.price && d.qty) {
			frappe.model.set_value(cdt, cdn, "total_without_tax", d.price*d.qty);
			frappe.model.set_value(cdt, cdn, "tax", d.total_without_tax*(d.tax_rate/100));
			frappe.model.set_value(cdt, cdn, "total_amount", d.total_without_tax+d.tax);

			var total = 0;
	        $.each(frm.doc.items || [], function (i, d) {
	            total += d.total_amount;
	        });
	        cur_frm.set_value("grand_total", total);

		}
	}
})



