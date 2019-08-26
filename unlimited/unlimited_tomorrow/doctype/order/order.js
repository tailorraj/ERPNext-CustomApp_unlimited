// Copyright (c) 2019, August Infotech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Tenant Order', {
	onload: function(frm,dt,dn) {
		if(frm.is_new()) {
			frm.set_value("appointment_time", null);
			frm.disable_save();
		}
	},
	refresh: function(frm) {

	},
	check_availability: function(frm) {

		var { employee, appointment_date} = frm.doc;

		if(!(employee && appointment_date)) {
			frappe.throw(__("Please select Employee and Appointment Date"));
		}

		// show booking modal
		frm.call({
			method: 'unlimited.unlimited_tomorrow.doctype.tenant_order.tenant_order.get_availability_data',
			args: {
				employee: employee,
				date: appointment_date
			},
			callback: (r) => {
				// console.log(r);
				var data = r.message;
				if(data.available_slots.length > 0) {
					show_availability(data);
				} else {
					show_empty_state();
				}
			}
		});

		// get end time of the day.
		var day_end_time_decimal = 0
		var day_end_time = 0
		
		frm.call({
			method: 'unlimited.unlimited_tomorrow.doctype.tenant_order.tenant_order.get_day_end_time',
			args: {
				employee: employee,
				date: appointment_date
			},
			callback: (r) => {
				if(r.message)
				{
					// console.log(timeToDecimal(r.message))
					day_end_time = r.message
					day_end_time_decimal = timeToDecimal(r.message)
					
				}
			}
		});
		
		// Show if barber is not available.
		function show_empty_state() {
			frappe.msgprint({
				title: __('Not Available'),
				message: __("Employee {0} not available on {1}", [frm.doc.employee_name.bold(), appointment_date.bold()]),
				indicator: 'red'
			});
		}

		// Show availability of employee.
		function show_availability(data) {
			
			var d = new frappe.ui.Dialog({
				title: __("Available slots"),
				fields: [{ fieldtype: 'HTML', fieldname: 'available_slots'}],
				primary_action_label: __("Book"),
				primary_action: function() {	

					// Check if selected time slot has enough time to complete the appointment else return. If time_per_appointment duration will conflict with appointed slots then it will return of throw the message.
					var start_time = timeToDecimal(selected_slot)
					var end_time = timeToDecimal(selected_slot) + flt(frm.doc.duration/60)

					for (var i = 0; i < button_list.length; i++) { 

						var button_time = timeToDecimal(button_list[i])
						
						if((start_time <= button_time) && (end_time > button_time))
						{
							var is_time_slot_disabled = $wrapper
							.find(`button[data-name="${button_list[i]}"]`)
							.attr('disabled')

							if (is_time_slot_disabled == 'disabled')
							{
								frappe.throw(__("Selected time slot has not enough time to complete appointment. Employee need" + " [ " +cstr(frm.doc.duration) + " minutes ]" +" to complete. Please select another time slot to book."))
							}
						}
					}

					// Check if selected time slot and time_per_appointment duration is conflict with the end time of the day. throw message if yes.
					if (end_time > day_end_time_decimal)
					{
						frappe.throw(__("Selected time slot has not enough time to complete appointment. Employee need" + " [ " +cstr(frm.doc.duration) + " minutes ]" +" to complete. Employee will not available after <b>" + cstr(day_end_time) + "</b>. Please select another time slot to book."))
					}

					frm.set_value('appointment_time', selected_slot);
					frm.set_value('duration', data.duration_of_service);

					// Set subject default if not filled up by user.
					// var subject = cstr(frm.doc.customer) + " [ Appointment handled by " + cstr(frm.doc.employee) + "]"
					// if(!frm.doc.subject)
					// {
					// 	frm.set_value('subject',  subject)
					// }
					
					d.hide();
					frm.save();
				}
			});

			var $wrapper = d.fields_dict.available_slots.$wrapper;
			var selected_slot = null;

			// disable dialog action initially
			d.get_primary_btn().attr('disabled', true);

			var current_date = new Date()
			var current_date_only = (current_date.getFullYear() + "-" + ("0" + (current_date.getMonth()+1)).slice(-2) + "-" + ("0" + current_date.getDate()).slice(-2)).toString()
			var current_time_in_decimal = timeToDecimal(current_date.getHours()+ ":" + current_date.getMinutes())

			var button_list = []

			// make buttons for each slot
			var slot_html = data.available_slots.map(slot => {

				var slot_time_in_decimal = timeToDecimal(slot.from_time)

				if (appointment_date == current_date_only)
				{
					// Show time slot which is greater than or equal to current time and don't show the past time slot.
					if (slot_time_in_decimal >= current_time_in_decimal)
					{
						button_list.push(slot.from_time);

						return `<button class="btn btn-default"
							data-name=${slot.from_time}
							style="margin: 0 10px 10px 0; width: 72px">
							${slot.from_time.substring(0, slot.from_time.length - 3)}
						</button>`;
					}
				}
				else
				{
					button_list.push(slot.from_time);

					return `<button class="btn btn-default"
							data-name=${slot.from_time}
							style="margin: 0 10px 10px 0; width: 72px">
							${slot.from_time.substring(0, slot.from_time.length - 3)}
						</button>`;
				}

			}).join("");

			if(!button_list.length)
			{

				frappe.msgprint({
					title: __('Not Available'),
					message: __("Employee {0} not available today after <b>{1}</b>", [frm.doc.employee_name.bold(), current_date.getHours()+ ":" + current_date.getMinutes()]),
					indicator: 'red'
				});
			}
			else
			{
				$wrapper
				.css('margin-bottom', 0)
				.addClass('text-center')
				.html(slot_html);
			}

			// disable buttons for which appointments are booked
			data.appointments.map(slot => {
		
				var start_time = flt(timeToDecimal(slot.appointment_time))
				var end_time = flt(timeToDecimal(slot.appointment_time)) + flt(slot.duration/60)

				for (var i = 0; i < button_list.length; i++) { 

					var button_time = timeToDecimal(button_list[i])

					if((start_time <= button_time) && (end_time > button_time))
					{
						$wrapper
						.find(`button[data-name="${button_list[i]}"]`)
						.attr('disabled', true);
					}
				}

			});

			// blue button when clicked
			$wrapper.on('click', 'button', function() {
				var $btn = $(this);
				$wrapper.find('button').removeClass('btn-primary');
				$btn.addClass('btn-primary');
				selected_slot = $btn.attr('data-name');

				// enable dialog action
				d.get_primary_btn().attr('disabled', null);
			});

			d.show();
		}
	}
});

// Function to convert the hours in decimal.
function timeToDecimal(t) {
    var arr = t.split(':');
    var dec = parseInt((arr[1]/6)*10, 10);

    return parseFloat(parseInt(arr[0], 10) + '.' + (dec<10?'0':'') + dec);
}

// Stop to select the back days date.
cur_frm.cscript.appointment_date = function(doc, dt, dn) {
	if (doc.appointment_date < frappe.datetime.get_today()) {
		cur_frm.set_value('appointment_date',null)
		frappe.msgprint(__("You can not select past date"));
		frappe.validated = false;
	}
}
