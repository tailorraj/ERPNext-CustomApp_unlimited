// Copyright (c) 2018, August Infotech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Unlimited Settings', {
	refresh: function(frm) {

	}
});

cur_frm.fields_dict.default_sales_person.get_query = function(doc,dt,dn) {
	return {
		 filters: { 'is_group': 0 }
	}
}
