// Copyright (c) 2018, August Infotech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Level of Amputee', {
	refresh: function(frm) {
		var html_for_image = '<img src="http://192.168.123.72:5050/files/coffe_logo_2.jpg" alt="Smiley face" height="42" width="42">'

		if (cur_frm.doc.__islocal) {
			$(frm.fields_dict['test_attach'].wrapper)
				.html(html_for_image);
		}
	}
});
