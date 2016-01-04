
var approval_required = false
frappe.ui.form.on("Request","onload",function(frm){
	frm.add_fetch('employee', 'employee_name', 'requester_name');
	frm.add_fetch('employee', 'cell_number', 'requester_contact_number');
	frm.add_fetch('employee', 'user_id', 'requester_email_id');
	frm.add_fetch('sub_request_category', 'approval_required', 'approval_required');
})

frappe.ui.form.on("Request","p_id",function(frm){
	if(cur_frm.doc.p_id){
		cur_frm.set_df_property("approver","read_only",0)
	}
})

cur_frm.fields_dict['sub_request_category'].get_query = function(doc) {
	return {
		filters: {
			'department_abbriviation': cur_frm.doc.department_abbriviation 
		}
	}
}

cur_frm.fields_dict['p_id'].get_query = function(doc) {
	return {
		filters: {
			'project_status': "Active" 
		}
	}
}

frappe.ui.form.on("Request","on_the_behalf_of",function(frm){
	if(cur_frm.doc.on_the_behalf_of == "Self"){
		return frappe.call({
			method: "help_desk.help_desk.doctype.request.request.get_user_details",
			callback: function(r) {
				console.log(r.message)
				cur_frm.doc.requester_name = r.message.requester_name
				cur_frm.doc.requester_email_id = r.message.email
				cur_frm.doc.requester_contact_number = r.message.cell_number
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

frappe.ui.form.on("Request", "refresh",function(frm){
	if(frm.doc.on_the_behalf_of){
		cur_frm.set_df_property("employee", "hidden",1);
		cur_frm.set_df_property("on_the_behalf_of", "hidden",1);	
    }
    if(cur_frm.doc.__islocal){
    	cur_frm.set_df_property("request_status","read_only",1)
    }
    else{
    	cur_frm.set_df_property("request_status","read_only",0)	
    }
	return frappe.call({
		method: "help_desk.help_desk.doctype.request.request.status_permission",
		args: {
			"doc":cur_frm.doc
		},
		callback: function(r) {
			if(r.message.valid == "true"){
				console.log(r.message)
				if(r.message.Existing_user == "Approver"){
					if((cur_frm.doc.approver_status == "Approved" || cur_frm.doc.approver_status == "Rejected" || cur_frm.doc.reopend == "Yes")&&(cur_frm.doc.editable_value == 0 || cur_frm.doc.editable_value == 2)){
						cur_frm.set_df_property("approver_status","read_only",1) 
						cur_frm.set_df_property("approver_comments","read_only",1)
			    		cur_frm.set_df_property("more_information","read_only",1)
			    		cur_frm.set_df_property("reason_for_rejection","read_only",1)
					}
					if(cur_frm.doc.reopend == "Yes" && cur_frm.doc.editable_value == 1){
						console.log("approver")
						cur_frm.set_df_property("approver_status","read_only",0)
						cur_frm.set_df_property("approver_comments","read_only",0)
			    		cur_frm.set_df_property("more_information","read_only",0)
			    		cur_frm.set_df_property("reason_for_rejection","read_only",0)
					}
					cur_frm.set_df_property("request_status","read_only",1)
					cur_frm.set_df_property("executor_status","read_only",1)
					cur_frm.set_df_property("additional_approver_status","read_only",1)
					cur_frm.set_df_property("priority","read_only",1)
			    	cur_frm.set_df_property("request_category","read_only",1)
			    	cur_frm.set_df_property("additional_approval_required","read_only",1)
			    	cur_frm.set_df_property("additional_approver","read_only",1)
					cur_frm.set_df_property("additional_approver_comments","read_only",1)
			    	cur_frm.set_df_property("more_info","read_only",1)
			    	cur_frm.set_df_property("reason_of_rejection","read_only",1)
			    	cur_frm.set_df_property("required_info","read_only",1)
			    	cur_frm.set_df_property("required_information","read_only",1)
			    	cur_frm.set_df_property("more_information_required","read_only",1)
				}


				if(r.message.Existing_user == "Executor"){
					if((cur_frm.doc.executor_status == "Resolved" || cur_frm.doc.reopend == "Yes")&&(cur_frm.doc.editable_value == 0 || cur_frm.doc.editable_value == 3 || cur_frm.doc.editable_value == 4)){
						cur_frm.set_df_property("executor_status","read_only",1)
						cur_frm.set_df_property("priority","read_only",1)
				    	cur_frm.set_df_property("request_category","read_only",1)
					}
					if(cur_frm.doc.executor_status == "Additional Approver Required"){
						console.log("correct")
						cur_frm.set_df_property("executor_status","read_only",1)
				    	cur_frm.set_df_property("additional_approver","read_only",1)
					}
					if(cur_frm.doc.additional_approver_status == "Approved" || cur_frm.doc.additional_approver_status == "Rejected"){
						cur_frm.set_df_property("executor_status","read_only",0)
				    	cur_frm.set_df_property("additional_approver","read_only",0)
					}
					if(cur_frm.doc.reopend == "Yes" && (cur_frm.doc.editable_value == 2 || cur_frm.doc.editable_value == 4)){
						cur_frm.set_df_property("executor_status","read_only",0)
						cur_frm.set_df_property("priority","read_only",0)
				    	cur_frm.set_df_property("request_category","read_only",0)
				    	cur_frm.set_df_property("additional_approver","read_only",0)
					}
					cur_frm.set_df_property("request_status","read_only",1)
					cur_frm.set_df_property("approver_status","read_only",1)
					cur_frm.set_df_property("additional_approver_status","read_only",1)
					cur_frm.set_df_property("approver_comments","read_only",1)
			    	cur_frm.set_df_property("more_information","read_only",1)
			    	cur_frm.set_df_property("reason_for_rejection","read_only",1)
			    	cur_frm.set_df_property("additional_approver_comments","read_only",1)
			    	cur_frm.set_df_property("more_info","read_only",1)
			    	cur_frm.set_df_property("reason_of_rejection","read_only",1)
			    	cur_frm.set_df_property("required_info","read_only",1)
			    	cur_frm.set_df_property("required_information","read_only",1)
				}


				if(r.message.Existing_user == "Ad_Approver"){
					if((cur_frm.doc.additional_approver_status == "Approved" || cur_frm.doc.additional_approver_status == "Rejected" || cur_frm.doc.reopend == "Yes")&&cur_frm.doc.editable_value == 0){
						cur_frm.set_df_property("additional_approver_status","read_only",1)
						cur_frm.set_df_property("additional_approver_comments","read_only",1)
				    	cur_frm.set_df_property("more_info","read_only",1)
				    	cur_frm.set_df_property("reason_of_rejection","read_only",1)
					}
					if(cur_frm.doc.reopend == "Yes" && cur_frm.doc.editable_value == 3){
						cur_frm.set_df_property("additional_approver_status","read_only",0)
						cur_frm.set_df_property("additional_approver_comments","read_only",0)
				    	cur_frm.set_df_property("more_info","read_only",0)
				    	cur_frm.set_df_property("reason_of_rejection","read_only",0)
					}
					cur_frm.set_df_property("request_status","read_only",1)
					cur_frm.set_df_property("approver_status","read_only",1)
					cur_frm.set_df_property("executor_status","read_only",1)
					cur_frm.set_df_property("priority","read_only",1)
			    	cur_frm.set_df_property("request_category","read_only",1)
			    	cur_frm.set_df_property("additional_approval_required","read_only",1)
			    	cur_frm.set_df_property("additional_approver","read_only",1)
			    	cur_frm.set_df_property("approver_comments","read_only",1)
			    	cur_frm.set_df_property("more_information","read_only",1)
			    	cur_frm.set_df_property("reason_for_rejection","read_only",1)
			    	cur_frm.set_df_property("required_info","read_only",1)
			    	cur_frm.set_df_property("required_information","read_only",1)
			    	cur_frm.set_df_property("more_information_required","read_only",1)
				}


				if(r.message.Existing_user == "Requester"){
					cur_frm.set_df_property("approver_status","read_only",1)
					cur_frm.set_df_property("executor_status","read_only",1)
					cur_frm.set_df_property("additional_approver_status","read_only",1)
					cur_frm.set_df_property("priority","read_only",1)
			    	cur_frm.set_df_property("request_category","read_only",1)
			    	cur_frm.set_df_property("additional_approval_required","read_only",1)
			    	cur_frm.set_df_property("additional_approver","read_only",1)
			    	cur_frm.set_df_property("approver_comments","read_only",1)
			    	cur_frm.set_df_property("more_information","read_only",1)
			    	cur_frm.set_df_property("reason_for_rejection","read_only",1)
			    	cur_frm.set_df_property("additional_approver_comments","read_only",1)
			    	cur_frm.set_df_property("more_info","read_only",1)
			    	cur_frm.set_df_property("reason_of_rejection","read_only",1)
			    	cur_frm.set_df_property("more_information_required","read_only",1)
				}	
			}
			else{
				//cur_frm.set_read_only();
			}	
		}
	})
});


frappe.ui.form.on("Request",{
	required_info:function(frm){
		this.validate_field(frm.doc,"Requester",frm)
	},
	required_information:function(frm){
		this.validate_field(frm.doc,"Requester",frm)
	},
	request_status:function(frm){
		this.validate_field(frm.doc,"Requester",frm)
	},
	approver_status:function(frm){
		this.validate_field(frm.doc,"Approver",frm)
	},
	approver_comments:function(frm){
		this.validate_field(frm.doc,"Approver",frm)	
	},
	more_information:function(frm){
		this.validate_field(frm.doc,"Approver",frm)
	},
	reason_for_rejection:function(frm){
		this.validate_field(frm.doc,"Approver",frm)
	},
	priority:function(frm){
		this.validate_field(frm.doc,"Executor",frm)
		this.set_due_date(frm)
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
	},
	p_id:function(frm){
		this.validate_pc_exists(frm)
	},
});

validate_pc_exists = function(frm){
	return frappe.call({
		method: "help_desk.help_desk.doctype.request.request.check_pc_exists",
		args:{
			"doc":cur_frm.doc
		},
		callback: function(r) {
			if (r.message){
				approval_required = true
			}			
		}
	})
}

validate_field = function(doc,check_for,frm){
		//logic to validate
		//if not valid user show message and reset the field

	return frappe.call({
		method: "help_desk.help_desk.doctype.request.request.check_for",
		args:{
			"check_for":check_for,
			"doc":cur_frm.doc
		},
		callback: function(r) {
			if(r.message){
				msgprint(r.message);
				cur_frm.reload_doc()
			}
			else if(!r.message && cur_frm.doc.reopend == "Yes"){
				cur_frm.set_value("editable_value",0)
				refresh_field('editable_value')
			}
		}
	})
}

set_due_date = function(frm){
	if(cur_frm.doc.priority){
		return frappe.call({
			method: "help_desk.help_desk.doctype.request.request.get_due_date",
			args: {
				"doc":frm.doc
			},
			callback: function(r){
				frm.set_value("due_date",r.message)
				refresh_field('due_date')
			}
		})
	}
}

cur_frm.fields_dict['approver'].get_query = function(doc, cdt, cdn) {
	if (approval_required){
		return {
			query: "help_desk.help_desk.doctype.request.request.get_approver_list",
			filters: {
				'project_id': doc.p_id,
				'doc' : cur_frm.doc
			}
		}
	}
	else{
		frappe.msgprint("Operational Matrix not linked")
	}
}

cur_frm.fields_dict['additional_approver'].get_query = function(doc, cdt, cdn) {
	if (cur_frm.doc.executor_status == "Additional Approver Required"){
		return {
			query: "help_desk.help_desk.doctype.request.request.filter_ad_approver",
			filters: {
				'doc': cur_frm.doc
			}
		}
	}
}


cur_frm.fields_dict['employee'].get_query = function(doc, cdt, cdn) {
	if (cur_frm.doc.on_the_behalf_of == "On The Behalf Of"){
		return {
			query: "help_desk.help_desk.doctype.request.request.filter_employee"
		}
	}
}

cur_frm.cscript.refresh = function(doc, cdt, cdn) {
	if(doc.docstatus == 0){
    	if(doc.request_status == "Close"){
       		cur_frm.add_custom_button(__("Re Open"),reopen_request)
 		}
	}
}	

reopen_request = function(frm) {
	cur_frm.set_value('reopend','Yes')
	cur_frm.doc.editable_value = 1
	cur_frm.doc.request_status = "Open"
	cur_frm.set_value('reopen_count',cur_frm.doc.reopen_count + 1)
	cur_frm.set_value('current_status',"Request Re opened")
	refresh_field(['request_status','reopen_count','current_status','editable_value'])
}