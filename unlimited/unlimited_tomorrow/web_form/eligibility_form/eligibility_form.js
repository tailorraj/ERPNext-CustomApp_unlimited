frappe.ready(function() {
	
	// Call to chek if user have permission to creat a new form or not.
	frappe.call({
		method: 'unlimited.unlimited_tomorrow.web_form.eligibility_form.eligibility_form.is_new_button_show',
		args: {
			user: frappe.session.user,
		},
		callback: function(res){
			if (res && !res.exc){
				if(res.message == 'False')
				{
					// Hide a "new" button if user is not permitted to create a new form.
					var new_button = $('.btn-new');
					if(new_button.length)
					{
						new_button[0].style.display = "none";
					}
					
					// Hide change image button if user has not permission to edit a new form.
					var change_attach_button = $('.change-attach');
					if(change_attach_button.length)
					{
						change_attach_button[0].remove();
					}

					// Clear the form html if user is not allowed to create a new form.
					var get_new_param = getUrlVars()["new"];
					if(get_new_param)
					{
						$(".page-content-wrapper").html("Sorry, currently you dont have a permission to create a new form.")
					}

					// Hide picture note.
					$("p.small,.picture_note").hide();

					// Get attch image url.
					var attach_image_url = $('p.small').find('a').attr('href');

					// Insert attach image html to show in webform.
					$( "<img src = "+ attach_image_url +" />" ).insertAfter($('p.small:has(a)').parent().find('label'));

				}
				else
				{
					$("[data-fieldname=rejection_reason]").show();

					// Get sample image.
					frappe.call({
						method: 'unlimited.unlimited_tomorrow.web_form.eligibility_form.eligibility_form.get_sample_image',
						args: {},
						callback: function(r){
							if (r.message){

								// Check if url has query string named "new".
								var has_new_param = getUrlVars()["new"];
								if(has_new_param)
								{
									// Show sample image html to show in new webform.
									$('span.small').find('div').prepend("<ul><li><strong>Sample Image</strong></li><ul class='sample-image' style='list-style-type: none;'><li><img title = 'sample image' height='100px' width='100px' src = "+ r.message +" /></li></ul></ul>");
								}
							}
						}
					});
				}
			}
		}
	});

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

	function hide_show_prosthetics_history()
	{
		if($("[data-fieldname=is_experience_prosthetics]").val() == 'No')
	    {
	    	$("[data-fieldname=prosthetics_history]").parent().hide();
	    	$("[data-fieldname=prosthetics_history]").parent().removeClass("has-error");
	    	$("[data-fieldname=prosthetics_history]").removeAttr("data-reqd");
	    }
	    else
	    {
	    	$("[data-fieldname=prosthetics_history]").parent().show();
	    	$("[data-fieldname=prosthetics_history]").parent().addClass("has-error");
	    	$("[data-fieldname=prosthetics_history]").attr("data-reqd",1);
	    }
	}

	hide_show_prosthetics_history();

	$("[data-fieldname=is_experience_prosthetics]").change(function(){
		hide_show_prosthetics_history();
	});

})