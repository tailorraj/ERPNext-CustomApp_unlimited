// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.ready(function() {

	frappe.call({
		method: 'unlimited.unlimited_tomorrow.web_form.eligibility_form.eligibility_form.has_approved_form',
		args: {
			user: frappe.session.user
		},
		callback: function(r){
			if (r.message){
				if(r.message == 'False'){
					$(".item-cart").empty();
				}
			}
		}
	});

});

