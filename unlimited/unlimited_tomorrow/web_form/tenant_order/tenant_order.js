frappe.ready(function() {


restrict_save_flag = 0
	// Function to get querystring
	function getUrlVars()
	{
	    var vars = [], hash;
	    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
	    for(var i = 0; i < hashes.length; i++)
	    {
	        hash = hashes[i].split('=');
	        vars.push(hash[0]);
	        vars[hash[0]] = hash[1];
	    }
	    return vars;
	}

	// disable new button if user has not approved eligibility form
	frappe.call({
		method: 'unlimited.unlimited_tomorrow.web_form.eligibility_form.eligibility_form.has_approved_form',
		args: {user: frappe.session.user},
		callback: function(r){
			if (r.message == 'False')
			{
				// Hide new button if user not have at least one approved eligibility form.
				var new_button = $('.btn-new');
				if(new_button.length)
				{
					new_button[0].style.display = "none";
				}

				// Replace html if user has not permitted to create new order form but directly hit the new form url from browser.
				var get_new_param = getUrlVars()["new"];
				if(get_new_param)
				{
					$(".page-content-wrapper").html("Sorry, currently you dont have a permission to create a new order form.")
				}
				var has_name_param = getUrlVars()["name"];
				if(has_name_param)
				{
					$(".page-content-wrapper").html("Sorry, currently you dont have a permission to view or edit order form.")
				}
			}
		}
	});
	
	// make api url dynamically
	// var hostname_with_port = window.location.href.split("/")[0] + "//" + window.location.href.split("/")[2]
	// var url_to_get_slots = hostname_with_port + "/api/method/unlimited.api.get_available_slots"


var final_slots =[]
var slot_to_delete=[]
var duration = 0
var default_employee=''


$( window ).load(function() {
	var get_new_param = getUrlVars()["new"];
	if(get_new_param){
		// set value of credit card information if already stored in customer
	frappe.call({
		method:'unlimited.unlimited_tomorrow.doctype.tenant_order.tenant_order.get_credit_card_info',
		args:{user: frappe.session.user},
		callback:function(data){
			if(data.message){
				$("[data-fieldname=name_on_card]").val(data.message['name'])
				$("[data-fieldname=credit_card_number]").val(data.message['card_number'])
				$("[data-fieldname=expiry_month]").val(data.message['ex_month'])
				$("[data-fieldname=expiry_year]").val(data.message['ex_year'])
				// console.log(data.message)
			}
		}
	})	
	}

// get default value of sale employee
  frappe.call({
  	method:'unlimited.unlimited_tomorrow.doctype.tenant_order.tenant_order.get_default_employee',
  	args:{},
  	callback:function(data){
  		default_employee = data.message
  	}
  })

})

$("[data-fieldname=appointment_date]").change(function(){

		final_slots =['']
		slot_to_delete=[]
		
		var current_date = new Date()
		var selected_date = $("[data-fieldname=appointment_date]").val()
		
		var res = selected_date.split("-");
		day = res[0]
		month = res[1]
		year = res[2]
		var date_string_only = year+'-'+month+'-'+day
		var selected_date_new_date = new Date(year+'-'+month+'-'+day)
		var current_date_only = (("0" + current_date.getDate()).slice(-2) + "-" + ("0" + (current_date.getMonth()+1)).slice(-2) + "-" + current_date.getFullYear()).toString()
		var current_date_only_inverse = new Date((current_date.getFullYear() + "-" + ("0" + (current_date.getMonth()+1)).slice(-2) + "-" + ("0" + current_date.getDate()).slice(-2)).toString())

// Restrict user to select the past date
		if (selected_date_new_date < current_date_only_inverse) 
		{

			$("[data-fieldname=available_time_slot]").find('option').remove()
			frappe.msgprint(__("You can not select past date"));
			return false;
		}



frappe.call({
		method: 'unlimited.unlimited_tomorrow.doctype.tenant_order.tenant_order.get_available_slots',
		args: {
			
				"date":date_string_only,
				"employee":default_employee

		},
			callback:function(data){
				// console.log(data.message)
					if (data.message)
					{
						
						

						$("[data-fieldname=available_time_slot]").find('option').remove()

						// msgprints if the selected date is holiday or employee on leave or employee is not available.
						if(data.message.is_holiday == 'Yes')
						{
							frappe.msgprint(__("<b>It's Holiday : </b> Selected date {0} is a holiday", [selected_date.bold()]));
						}
						else if(data.message.is_on_leave == 'Yes')
						{
							frappe.msgprint(__("<b>On Leave : </b> Appointment slot is not available on leave on selected date {0}", [selected_date.bold()]));
						}
						else if(data.message.is_employee_available == 'No')
						{
							frappe.msgprint(__("<b>Not Available : </b>Appointment slot is not available on selected date {0}", [selected_date.bold()]));
						}
						
						if(data.message.is_on_leave == 'No' && data.message.is_holiday == 'No' && data.message.is_employee_available == 'Yes')
						{	
							
							for (i = 0; i < data.message.available_slots.length; i++) {

								var slot_time_in_decimal = timeToDecimal(data.message.available_slots[i].from_time)
								var current_time_in_decimal = timeToDecimal(current_date.getHours()+ ":" + current_date.getMinutes())
								// fill the select box with the time slots
										
									// disable slot of current date before current time
									if(selected_date == current_date_only){

										if ( slot_time_in_decimal >= current_time_in_decimal )
										{
											final_slots.push(data.message.available_slots[i]['from_time'])
										}
									}
									else{
										final_slots.push(data.message.available_slots[i]['from_time'])
									}


								}
								

								for (i = 0; i < data.message.appointments.length; i++){
									duration = data.message.appointments[i].duration
								  	var start_time = flt(timeToDecimal(data.message.appointments[i].appointment_time))
									var end_time = flt(timeToDecimal(data.message.appointments[i].appointment_time)) + flt(data.message.appointments[i].duration/60) 

								

									for (j = 0; j < final_slots.length; j++){
										var slot = timeToDecimal(final_slots[j])
										
										if((start_time <= slot) && (end_time > slot)){
											
											slot_to_delete.push(final_slots[j])
											
											
										}
										
									}
								}

								

								final_slots = final_slots.filter( function( el ) {
								  return !slot_to_delete.includes( el );
								});

								

								for (var i = final_slots.length - 1; i >= 0; i--) {
									$("[data-fieldname=available_time_slot]").append("<option value='" + final_slots[i]+ "'" + (i == 0?"selected = 'selected'":'') + ">" + final_slots[i] + "</option>");
								}
								
							}
							
							
						}
					}
				

			})
})
	
// Function to convert the hours in decimal.
function timeToDecimal(t) {
    var arr = t.split(':');
    var dec = parseInt((arr[1]/6)*10, 10);

    return parseFloat(parseInt(arr[0], 10) + '.' + (dec<10?'0':'') + dec);
}

// disable conflicted time slot
$("[data-fieldname=available_time_slot]").change(function(){

 if($("[data-fieldname=available_time_slot]").val()){
 		var selected_slot = $("[data-fieldname=available_time_slot]").val()

 					var start_time = timeToDecimal(selected_slot)
					var end_time = timeToDecimal(selected_slot) + flt(duration/60)

					for (var i = 0; i < slot_to_delete.length; i++) { 

						var slot_time = timeToDecimal(slot_to_delete[i])
						
						if((start_time <= slot_time) && (end_time > slot_time)){
							frappe.msgprint(__("Selected time slot has not enough time to complete appointment. Employee need" + " [ " +cstr(duration) + " minutes ]" +" to complete. Please select another time slot to book."))
							restrict_save_flag = 1
							
						}
						else{
						restrict_save_flag = 0
						}
					}

 }

})

// disable end slot of emloyee
$("[data-fieldname=available_time_slot]").change(function(){

// set value of time field on change of available slot
$("[data-fieldname=appointment_time]").val($("[data-fieldname=available_time_slot]").val())

 if($("[data-fieldname=available_time_slot]").val()){
 			
 			frappe.call({
			method: 'unlimited.unlimited_tomorrow.doctype.tenant_order.tenant_order.get_day_end_time',
			args: {
				employee:default_employee,
				date: $("[data-fieldname=appointment_date]").val()
			},
			callback: (r) => {
				if(r.message){
					var selected_slot = $("[data-fieldname=available_time_slot]").val()
					var end_time = timeToDecimal(selected_slot) + flt(duration/60)
					var emp_end_time = timeToDecimal(r.message)
					
					if (end_time > emp_end_time){
						frappe.msgprint(__("Selected time slot has not enough time to complete appointment. Employee need" + " [ " +cstr(duration) + " minutes ]" +" to complete. Employee will not available after <b>" + cstr(r.message) + "</b>. Please select another time slot to book."))
						restrict_save_flag = 1
						
					}
					else{
						restrict_save_flag = 0
					}
					
					
					
				}
			}
			});
 		
 }

})

var has_name_param = getUrlVars()["name"];
if(has_name_param)
{
	$('input, textarea, select').attr('readonly','readonly');
	$(".attach-input-wrap").remove();
	$("[data-fieldname=available_time_slot]").parent().hide();
	$('button').remove();
	
	// $("h5:contains('Credit Card Details')").parent.hide();
}

var get_new_param = getUrlVars()["new"];
if(get_new_param)
{
	$("[data-fieldname=appointment_time]").parent().hide();
}

// credit card validation of selected month and year
$("[data-fieldname=expiry_year]").change(function(){

	var today,someday;
	today = new Date();
	var selected_month = $("[data-fieldname=expiry_month]").val();
	var selected_year = $("[data-fieldname=expiry_year]").val();
	someday = new Date();
	someday.setFullYear(selected_year, selected_month, 1);

	if (someday < today) {
		frappe.msgprint(__("The expiry date is before today's date. Please select a valid expiry date"));
	   return false;
	}

})



});