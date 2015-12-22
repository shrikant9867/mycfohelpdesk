frappe.ui.form.on("Department Name","department_abbriviation",function(frm){
	console.log(cur_frm.doc.department_abbriviation.length)
	if(cur_frm.doc.department_abbriviation.length > 3){
		msgprint(__("Abbriviation should not greater than three characters"))
		cur_frm.doc.department_abbriviation = "",
		refresh_field("department_abbriviation")
	}
	var regex = /^[a-zA-Z]*$/
	if (!regex.test(cur_frm.doc.department_abbriviation)){
		msgprint(__("Only Alphabets Are Allowed"))
		cur_frm.doc.department_abbriviation = "",
		refresh_field("department_abbriviation")
	}
})

frappe.ui.form.on("Department Name","name_of_department",function(frm){
	var regex = /^[a-zA-Z]*$/
	if(!regex.test(cur_frm.doc.name_of_department)) {
		msgprint(__("Only Alphabets Are Allowed"))
		cur_frm.doc.name_of_department = "",
		refresh_field("name_of_department")
	}
})	