frappe.ui.form.on("Sub Request Category","sub_request_name",function(frm){
	var regex = /^[a-zA-Z, ]*$/
	if(!regex.test(cur_frm.doc.sub_request_name)) {
		msgprint(__("Only Alphabets Are Allowed"))
		cur_frm.doc.sub_request_name = "",
		refresh_field("sub_request_name")
	}
})	