/*frappe.ui.form.on("New Request","s_req_name",function(frm){
frm.add_fetch('s_req_name', 'approver', 'approver');
frm.add_fetch('s_req_name', 'p_name', 'project_name');
})*/

frappe.ui.form.on("New Request","employee",function(frm){
frm.add_fetch('employee', 'employee_name', 'employee_name');
frm.add_fetch('employee', 'cell_number', 'cell_number');
frm.add_fetch('employee', 'user_id', 'personal_email');
})


frappe.ui.form.on("New Request","on_the_behalf_of",function(frm){
	if(cur_frm.doc.on_the_behalf_of == "Self"){
		console.log("self")
		return frappe.call({
			method: "help_desk.help_desk.doctype.new_request.new_request.make_self_entry",
			callback: function(r) {
				console.log(r.message[0][0])
				cur_frm.doc.employee_name = r.message[0][0]
				cur_frm.doc.personal_email = r.message[0][1]
				cur_frm.doc.cell_number = r.message[0][2]
				cur_frm.refresh_fields()
			} 
		})

		}
	
});

cur_frm.cscript.refresh = function(doc, cdt, cdn) {
	if(doc.s_req_name){	
		cur_frm.set_df_property("status", "editable",1);
		cur_frm.set_df_property("d_abb", "read_only",1);
		cur_frm.set_df_property("s_req_name", "read_only",1);
		cur_frm.set_df_property("sub", "read_only",1);
		cur_frm.set_df_property("iss_des", "read_only",1);
		cur_frm.set_df_property("project_name", "read_only",1);
		cur_frm.set_df_property("approver", "read_only",1);
    }
}    
	/*}
	else(doc.s_req_name)
	{
		cur_frm.set_read_only();
	}*/
 
/*frappe.provide("help_desk.new_request");

frappe.ui.form.on("New Request", {
	refresh: function(frm) {
		console.log("onform")
		if (frm.doc.__islocal) {
			frm.add_custom_button(__('New Request'), function() {
				return help_desk.new_request.new_request(frm);
			});
		}
	}
})		


$.extend(help_desk.new_request, {
	new_request: function(frm) {
		console.log("after click")
		this.dialog = new frappe.ui.Dialog({
			title: __("New Request Details"),
			fields: [
			{fieldtype: "Data", fieldname: "employee_name", label: __("Full Name"), reqd: 1},
				{fieldtype: "HTML", fieldname: "request_html"},
				{fieldtype: "Link", fieldname: "employee_name", label: __("Full Name"), reqd: 1,
					options: "Employee"},
				
			]
		});

		this.dialog.show();
		console.log(this.dialog.fields_dict.request_html.$input)
		console.log($(this.dialog.fields_dict))
		console.log($(this.dialog.body).find("[data-fieldname=request_html]"))
		$(this.dialog.body).find("[data-fieldname=request_html]").html('<form><input type="radio" name="same" id="other"> Self <br>\
					<input type="radio" name="same" id="self"> Others</form>');
		$("#self").click(function(){
        $.fn.confirmInput();
    });			       
		console.log($(this.dialog.body).find("#self"))			                                  
		
	},
});*/			