frappe.ui.form.on("Request Category","request_category",function(frm){
	var regex = /^[a-zA-Z, ]*$/
	if(!regex.test(cur_frm.doc.request_category)) {
		msgprint(__("Only Alphabets Are Allowed"))
		cur_frm.doc.request_category = "",
		refresh_field("request_category")
	}
})	