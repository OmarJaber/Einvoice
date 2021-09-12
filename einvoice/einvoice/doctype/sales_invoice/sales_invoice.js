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

	}
});


frappe.ui.form.on('Sales Invoice Item', {
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
	        $.each(frm.doc.items || [], function (i, d) {
	            total += d.amount;
	        });
	        cur_frm.set_value("grand_total", total);

		}
	},
	qty: function(frm, cdt, cdn){
		var d = locals[cdt][cdn];
		if(d.price && d.qty) {
			frappe.model.set_value(cdt, cdn, "total", d.price*d.qty);
			frappe.model.set_value(cdt, cdn, "tax_value", (d.rate/100.0)*d.total);
			frappe.model.set_value(cdt, cdn, "amount", d.total+d.tax_value);

			var total = 0;
	        $.each(frm.doc.items || [], function (i, d) {
	            total += d.amount;
	        });
	        cur_frm.set_value("grand_total", total);

		}
	}
})


