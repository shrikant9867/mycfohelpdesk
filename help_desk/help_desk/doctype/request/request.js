
var approval_required = false
frappe.ui.form.on("Request","onload",function(frm){
	frm.add_fetch('employee', 'employee_name', 'requester_name');
	frm.add_fetch('employee', 'cell_number', 'requester_contact_number');
	frm.add_fetch('employee', 'user_id', 'requester_email_id');
	frm.add_fetch('sub_request_category', 'approval_required', 'approval_required');
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
				cur_frm.doc.requester_name = r.message.requester_name
				cur_frm.doc.requester_email_id = r.message.email
				cur_frm.doc.requester_contact_number = r.message.cell_number
				cur_frm.refresh_fields()
			} 
		})
	}		
	if(cur_frm.doc.on_the_behalf_of == "Others"){
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
		/*doc:cur_frm.doc,*/
		args: {
			"doc":cur_frm.doc
		},
		callback: function(r) {
			if(r.message.valid == "true"){
				console.log(r.message)
				if(r.message.Existing_user == "Approver"){
					if((cur_frm.doc.approver_status == "Approved" || cur_frm.doc.approver_status == "Rejected")&&(cur_frm.doc.editable_value != 1)){	
						cd_fields = ['approver_status','approver_comments','more_information','reason_for_rejection']
						make_fields_read_only(cd_fields)
					}
					cd_fields1 = ['request_status','additional_approver_status','executor_status','priority','request_category','additional_approval_required',
									'additional_approver','additional_approver_comments','more_info','reason_of_rejection','required_info','required_information',
									'more_information_required','more_info_of_executor']
					make_fields_read_only(cd_fields1)
				}

				if(r.message.Existing_user == "Executor"){
					if(cur_frm.doc.executor_status == "Resolved"){
						cd_fields = ['executor_status','priority','request_category']
						make_fields_read_only(cd_fields)
					}
					if(cur_frm.doc.executor_status == "Additional Approver Required"){
						cd_fields = ['executor_status','additional_approver']
						make_fields_read_only(cd_fields)
					}
					if(cur_frm.doc.editable_value == 1 || cur_frm.doc.editable_value == 2 || cur_frm.doc.editable_value == 4){
						cd_fields = ['executor_status','priority','request_category','additional_approver']
						make_fields_editable(cd_fields)
					}
					cd_fields1 = ['request_status','approver_status','additional_approver_status','approver_comments','more_information','reason_for_rejection',
								'reason_of_rejection','additional_approver_comments','more_info','required_info','required_information']
					make_fields_read_only(cd_fields1)
				}

				if(r.message.Existing_user == "Ad_Approver"){				
					if((cur_frm.doc.additional_approver_status == "Approved" || cur_frm.doc.additional_approver_status == "Rejected")&&(cur_frm.doc.editable_value != 3)){
						cd_fields = ['additional_approver_status','additional_approver_comments','more_info','reason_of_rejection']
						make_fields_read_only(cd_fields)
					}
					cd_fields1 = ['request_status','approver_status','executor_status','priority','request_category','additional_approval_required',
									'additional_approver','approver_comments','more_information','reason_for_rejection','required_info','required_information','more_information_required','more_info_of_executor']
					make_fields_read_only(cd_fields1)
				}

				if(r.message.Existing_user == "Requester"){
					cd_fields = ['approver_status','executor_status','additional_approver_status','priority','request_category','additional_approval_required','additional_approver','approver_comments',
									'more_information','reason_for_rejection','additional_approver_comments','reason_of_rejection','more_information_required','more_info_of_executor','more_info']
					make_fields_read_only(cd_fields)
				}	
			}	
		}
	})
});


make_fields_read_only = function(cd_fields){
	$.each(cd_fields, function(index, value){
		cur_frm.set_df_property(value, "read_only", 1);	
	})
}

make_fields_editable = function(cd_fields){
	$.each(cd_fields, function(index, value){
		cur_frm.set_df_property(value, "read_only", 0);	
	})
}

frappe.ui.form.on("Request",{
	customer:function(frm){
		this.validate_pc_exists(frm)
		},
/*	p_id:function(frm){
		this.validate_pc_exists(frm)
		},*/
	priority:function(frm){
		this.set_due_date(frm)
	}	
});

validate_pc_exists = function(frm){
	return frappe.call({
		method: "help_desk.help_desk.doctype.request.request.check_pc_exists",
		args:{
			"doc":cur_frm.doc
		},
		callback: function(r) {
			console.log(r.message)
			if (r.message){
				approval_required = true
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
	if (approval_required = true){
		console.log("in if")
		return {
			query: "help_desk.help_desk.doctype.request.request.get_approver_list",
			filters: {
				/*'project_id': doc.p_id,*/
				'customer': doc.customer,
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


cur_frm.fields_dict['employee'].get_query = function(doc) {
	if (cur_frm.doc.on_the_behalf_of == "Others"){
		return {
			query: "help_desk.help_desk.doctype.request.request.filter_employee"
		}
	}
}

/*cur_frm.cscript.refresh = function(doc, cdt, cdn) {
	if(doc.docstatus == 0){
    	if(doc.request_status == "Close"){
       		cur_frm.add_custom_button(__("Re Open"),reopen_request)
 		}
	}
}*/

frappe.ui.form.on("Request","request_status",function(frm){
	if(cur_frm.doc.request_status == "Close"){
		cur_frm.set_df_property("request_status","read_only",1)
		cur_frm.save();
	}	
})

cur_frm.cscript.refresh = function(frm) {
	if(cur_frm.perm[0].write){
    	if(cur_frm.doc.request_status == "Close"){
    		cur_frm.set_df_property("request_status","read_only",1)
       		cur_frm.add_custom_button("Re open", function() {
				reopen_request(frm);
				cur_frm.save();
 			});
 		}	
	}
}	

reopen_request = function(frm) {
	cur_frm.set_value('reopend','Yes')
	cur_frm.doc.editable_value = 1
	cur_frm.doc.request_status = "Open"
	cur_frm.set_value('reopen_count',cur_frm.doc.reopen_count + 1)
	cur_frm.set_value('current_status',"Request Re opened")
	cur_frm.set_value('allocated_to',"Create")
	refresh_field(['request_status','reopen_count','current_status','editable_value','allocated_to'])
}