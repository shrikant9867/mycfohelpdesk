frappe.ui.form.on("Department Name","department_abbriviation",function(frm){
	console.log(cur_frm.doc.department_abbriviation.length)
	if(cur_frm.doc.department_abbriviation.length > 3){
		msgprint(__("Abbriviation should not greater than three characters"))
		cur_frm.doc.department_abbriviation = "",
		refresh_field("department_abbriviation")
		}
	})	