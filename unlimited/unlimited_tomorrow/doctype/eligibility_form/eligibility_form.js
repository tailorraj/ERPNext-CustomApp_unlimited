// Copyright (c) 2018, August Infotech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Eligibility Form', {
	refresh: function(frm) {
		if(frm.doc.docstatus == 0 && frm.doc.workflow_state == 'In Progress' && frappe.user.has_role(['Eligibility Form Manager'])) {
			cur_frm.add_custom_button(__('Reject'), cur_frm.cscript['Reject Request']).addClass("btn-danger");;
		}
	}
});

cur_frm.cscript['Reject Request'] = function(){
	var dialog = new frappe.ui.Dialog({
		title: "Reject Request",
		fields: [
			{"fieldtype": "Small Text", "label": __("Rejection Reason"), "fieldname": "rejection_reason", "reqd": 1 },
			{"fieldtype": "Button", "label": __("Update"), "fieldname": "update"},
		]
	});

	dialog.fields_dict.update.$input.click(function() {
		var args = dialog.get_values();
		
		if(!args) return;

		frappe.call({
			method: "reject_request",
			doc: cur_frm.doc,
			args: {rejection_reason:args.rejection_reason},
			callback: function(r) {
				if(r.exc) {
					frappe.msgprint(__("There are some error. Form can't be rejected."));
					return;
				}
				if (r && !r.exc){
					frappe.call({
						method: 'frappe.core.doctype.communication.email.make',
						args: {
							doctype: cur_frm.doctype,
							name: cur_frm.docname,
							subject: format(__('Reason for {0}'), [cur_frm.doc.workflow_state]),
							content: args.rejection_reason,
							send_mail: false,
							send_me_a_copy: false,
							communication_medium: 'Other',
							sent_or_received: 'Sent'
						},
						callback: function(res){
							cur_frm.reload_doc();
						}
					});
				}
				dialog.hide();
				cur_frm.refresh();
			},
			btn: this
		})

	});
	dialog.show();
}

// frappe.ui.form.on("Eligibility Form", "before_save", function(frm, cdt, cdn){
// 		if (frm.doc.workflow_state== "Rejected" && frm.doc.workflow_state.indexOf("Rejected") == 0){
// 			frappe.prompt([
// 				{
// 					fieldtype: 'Small Text',
// 					reqd: 1,
// 					fieldname: 'reason',
// 					label: 'Reason for rejecting'
// 				}],
// 				function(args){
// 					validated = 1;
// 					frappe.call({
// 						method: 'frappe.core.doctype.communication.email.make',
// 						args: {
// 							doctype: frm.doctype,
// 							name: frm.docname,
// 							subject: format(__('Reason for {0}'), [frm.doc.workflow_state]),
// 							content: args.reason,
// 							send_mail: false,
// 							send_me_a_copy: false,
// 							communication_medium: 'Other',
// 							sent_or_received: 'Sent'
// 						},
// 						callback: function(res){
// 							if (res && !res.exc){
// 								frappe.call({
// 									method: 'frappe.client.set_value',
// 									args: {
// 										doctype: frm.doctype,
// 										name: frm.docname,
// 										fieldname: 'rejection_reason',
// 										value: frm.doc.rejection_reason ?
// 											[frm.doc.rejection_reason, frm.doc.workflow_state].join('\n') : frm.doc.workflow_state
// 									},
// 									callback: function(res){
// 										if (res && !res.exc){
// 											frm.reload_doc();
// 										}
// 									}
// 								});
// 							}
// 						}
// 					});
// 				},
// 				__('Reason for ') + frm.doc.workflow_state,
// 				__('End as Rejected')
// 			)
// 		}
// 	});
