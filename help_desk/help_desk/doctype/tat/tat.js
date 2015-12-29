frappe.ui.form.on("TAT","tat",function(frm){
	if(cur_frm.doc.tat <= 0){
		cur_frm.doc.tat = ""
		refresh_field("tat")
		msgprint(__("Please Enter Positive Value For TAT"))
		frm.reload();	
	}
})

