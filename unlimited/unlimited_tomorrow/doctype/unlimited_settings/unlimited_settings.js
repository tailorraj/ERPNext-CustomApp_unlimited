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

cur_frm.cscript.allow_google_calendar_access= function(doc,dt,dn){
		frappe.call({
			method: "unlimited.unlimited_tomorrow.doctype.tenant_order.tenant_order.google_callback",
			args: {},
			callback: function(r) {
				if (r.message){
					window.open(r.message.url);
				}
			}
		})
}
