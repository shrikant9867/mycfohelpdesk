frappe.ui.form.on("Request","onload",function(frm){
	frm.add_fetch('employee', 'employee_name', 'requester_name');
	frm.add_fetch('employee', 'cell_number', 'requester_contact_number');
	frm.add_fetch('employee', 'user_id', 'requester_email_id');
	frm.add_fetch('sub_request_category', 'approval_required', 'approval_required');
	/*frm.add_fetch('sub_request_category', 'executer', 'role');*/
})

frappe.ui.form.on("Request","onload" ,function(frm){
	cur_frm.fields_dict.sub_request_category.get_query = function(doc) {
		return {
			filters: {
				'department_abbriviation': cur_frm.doc.department_abbriviation 
			}
		}
	}
})

frappe.ui.form.on("Request","onload" ,function(frm){
	cur_frm.fields_dict.p_id.get_query = function(doc) {
		return {
			filters: {
				'project_status': "Active" 
			}
		}
	}
})

/*frappe.ui.form.on("Request","onload" ,function(frm){
	cur_frm.fields_dict.approver.get_query = function(doc) {
		return{
			filters: {
				'operational_and_project_details' : role
			}
		}
	}
})	*/


frappe.ui.form.on("Request","on_the_behalf_of",function(frm){
	if(cur_frm.doc.on_the_behalf_of == "Self"){
		console.log("self")
		return frappe.call({
			method: "help_desk.help_desk.doctype.request.request.get_user_details",
			callback: function(r) {
				cur_frm.doc.requester_name = r.message.first_name
				cur_frm.doc.requester_email_id = r.message.email
				cur_frm.doc.requester_contact_number = r.message.requester_contact_number
				cur_frm.refresh_fields()
			} 
		})
	}		
	if(cur_frm.doc.on_the_behalf_of == "On The Behalf Of"){
		frm.doc.requester_name = ""
		frm.doc.requester_email_id = ""
		frm.doc.requester_contact_number = ""
		cur_frm.refresh_field("requester_name")
		cur_frm.refresh_field("requester_email_id")
		cur_frm.refresh_field("requester_contact_number")
	}	
});

frappe.ui.form.on("Request","priority",function(frm){
	if(cur_frm.doc.priority){
		console.log("High")
		return frappe.call({
			method: "help_desk.help_desk.doctype.request.request.get_due_date",
			args: {
				"doc":cur_frm.doc
			},
			callback: function(r){
				console.log(r.message)
				cur_frm.doc.due_date = r.message
				cur_frm.refresh_fields()
			}
		})
	}
});

/*frappe.ui.form.on("Request","approver",function(frm){
	if(cur_frm.doc.approver){
		console.log("approver1")
		return frappe.call({
			method: "help_desk.help_desk.doctype.request.request.get_approver_list",
			args: {
				"doc":cur_frm.doc
			},
			callback: function(r){
				console.log(r.message)
				cur_frm.doc.approver = r.message
			} 
		})
	}
});*/

cur_frm.fields_dict['approver'].get_query = function(doc, cdt, cdn) {
	return {
		query: "help_desk.help_desk.doctype.request.request.get_approver_list",
		filters: {
			'project_id': doc.p_id
		}
	}
}



cur_frm.cscript.refresh = function(doc, cdt, cdn) {
	if(doc.on_the_behalf_of){
		cur_frm.set_df_property("employee", "hidden",1);
		cur_frm.set_df_property("on_the_behalf_of", "hidden",1);	
    }
    if(doc.approver_status == "Approved" || doc.approver_status == "Rejected" ||
    	doc.approver_status == "More Info Required"){
    	cur_frm.set_df_property("approver_status","read_only",1)
    	cur_frm.set_df_property("approver_comments","read_only",1)
    	cur_frm.set_df_property("more_information","read_only",1)
    	cur_frm.set_df_property("reason_for_rejection","read_only",1)
    }
    if(doc.additional_approver_status == "Approved" || doc.additional_approver_status == "Rejected" ||
	     doc.additional_approver_status == "More Info Required"){
    	cur_frm.set_df_property("additional_approver_status","read_only",1)
    	cur_frm.set_df_property("additional_approver_comments","read_only",1)
    	cur_frm.set_df_property("more_info","read_only",1)
    	cur_frm.set_df_property("reason_of_rejection","read_only",1)
    }
   
    if(doc.priority){
    	cur_frm.set_df_property("priority","read_only",1)
    	cur_frm.set_df_property("due_date","read_only",1)
    	cur_frm.set_df_property("request_category","read_only",1)
    	cur_frm.set_df_property("additional_approval_required","read_only",1)
    	cur_frm.set_df_property("additional_approver","read_only",1)
    	cur_frm.set_df_property("more_information_required","read_only",1)
    	cur_frm.set_df_property("executor_status","read_only",1)

    }
    if(doc.requester_email_id){
    	cur_frm.set_df_property("more_info_required","read_only",1)
    }
    if(doc.docstatus == 0){
    	if(doc.request_status == "Close"){
       		cur_frm.add_custom_button(__("Re Open"),new_request)
 		}
	}
    refresh_field("allocated_to")
}	

frappe.ui.form.on("Request",{
	more_info_required:function(frm){
		this.validate_field(frm.doc,"Requester",frm)
	},
	request_status:function(frm){
		this.validate_field(frm.doc,"Requester",frm)
	},
	approver_status:function(frm){
		this.validate_field(frm.doc,"Approver",frm)
	},
	approver_comments:function(frm){
		this.validate_field("Approver")	
	},
	more_information:function(frm){
		this.validate_field(frm.doc,"Approver",frm)
	},
	reason_for_rejection:function(frm){
		this.validate_field("Approver")
	},
	priority:function(frm){
		this.validate_field(frm.doc,"Executor",frm)
	},
	due_date:function(frm){
		this.validate_field(frm.doc,"Executor",frm)
	},
	request_category:function(frm){
		this.validate_field(frm.doc,"Executor",frm)
	},
	executor_status:function(frm){
		this.validate_field(frm.doc,"Executor",frm)
	},
	more_information_required:function(frm){
		this.validate_field(frm.doc,"Executor",frm)
	},
	additional_approval_required:function(frm){
		this.validate_field(frm.doc,"Executor",frm)	
	},
	additional_approver:function(frm){
		this.validate_field(frm.doc,"Executor",frm)
	},
	additional_approver_status:function(frm){
		this.validate_field(frm.doc,"Additional Approver",frm)
	},
	additional_approver_comments:function(frm){
		this.validate_field(frm.doc,"Additional Approver",frm)
	},
	more_info:function(frm){
		this.validate_field(frm.doc,"Additional Approver",frm)
	},
	reason_of_rejection:function(frm){
		this.validate_field(frm.doc,"Additional Approver",frm)
	}
});

validate_field = function(doc,check_for,frm){
	console.log(check_for)
		//logic to validate
		//if not valid user show message and reset the field

	return frappe.call({
		method: "help_desk.help_desk.doctype.request.request.check_for",
		args:{
			"check_for":check_for,
			"doc":doc
		},
		callback: function(r) {
			if(r.message){
				msgprint(r.message);
				cur_frm.reload_doc()
			}
		}
		

	})
}

new_request = function() {
	console.log("new_request")
	frappe.model.open_mapped_doc({
		method: "help_desk.help_desk.doctype.request.request.make_new_request",
		frm: cur_frm
	})
}