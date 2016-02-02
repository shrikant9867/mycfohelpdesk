# -*- coding: utf-8 -*-
# Copyright (c) 2015, Indictrans and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import itertools
import json
from frappe.utils import get_link_to_form,get_url_to_form,comma_or,get_fullname,nowdate, getdate,cstr
from frappe.model.naming import make_autoname
from frappe import throw, _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe import msgprint
from frappe.utils import now_datetime
from datetime import datetime, timedelta
import frappe.share

"""
	Purpose:Manage tickets.
	>Roles:
		1.Requestor(Creator of ticket)
		2.Approver(Approver of ticket)
		3.Executor(Executor of ticket)
		4.Additional Approver(if additional approver required then additional approver will approve ticket)
	>Functionilty:
		1.Tickets can be created by user for self or for onbehalf of others.
		2.based on subrequest ticket are sent to approver or executer.
		3.Approver will approve or reject ticket and also can ask for more info to approve ticket.
		4.Executor will set proirity of ticket,request type and change the status of to completed or wip or on hold.
			he can also set additional approver.
		5.Additional Approver will approve or reject ticket and also can ask for more info to approve ticket.
	>Notifications:
		1.After Each stage send notifications.
"""
class Request(Document):
	def autoname(self):
		if self.request_status == "Open":
			if not self.support_id:
				self.support_id = make_autoname(self.department_abbriviation.upper()+ ' - ' +'.#####') 
				self.name = self.support_id
			elif self.support_id:
				self.name = self.support_id

	def validate(self):	
		pass

	def on_update(self):
		self.build_notification()
		self.close_request()
		if self.reopend == "Yes" and self.reopen_count == 0:
			self.send_mail_of_reopen()
		
	def build_notification(self):
		"""
			Decide whom to notify
		"""
		if self.allocated_to == "Create":
			self.notify_to_approver_or_executor()
			self.add_requetor_and_ticket_details_to_comment()
		elif self.allocated_to == 'Approver':
			self.perform_approver_operations()
			self.add_approver_comments()
		elif self.allocated_to == 'Executor':
			self.perform_executor_operations()
			self.add_executor_comments()
		elif self.allocated_to == 'Ad Approver':
			self.perform_additional_approver_operations()	
			self.add_addn_approver_comments()
		elif self.allocated_to == "Requester":
			self.add_requester_comments()
			self.perform_requester_operations()

	def send_mail_of_reopen(self):
		if self.approver:
			approver = frappe.get_doc("Employee",self.approver)
			self.notify_user([approver.user_id],"Request Reopened","Request Reopened By Requester")
		executor = self.get_executer_list()
		self.notify_user([approver.user_id,self.requester_email_id,(", ".join(executor))],"Request Reopened","Request Reopen By Requester")		

	def notify_to_approver_or_executor(self):
		"""
			if subrequest has approver then send notification to approver else send notification to executer 
			after sending mail change status of allocated_to to approver or executer
		"""
		
		if self.approval_required == 'Yes':
			"""
				send mail to approver and requestor
				["approver@gmail.com","requestor@gmail.com"]
			"""
			if self.approver:
				approver = frappe.get_doc("Employee",self.approver)
				self.notify_user([approver.user_id,self.requester_email_id],"Request Created","Request has been created")
				self.allocated_to = "Approver"
				frappe.db.set_value("Request",self.name,"allocated_to","Approver")
				self.current_status = "Request Sent To Approver"
				frappe.db.set_value("Request",self.name,"current_status","Request Sent To Approver")
				self.share_document(approver.user_id)
				self.share_document(self.requester_email_id)
				comment = """Created Request and assigned to Approver:{approver}""".format(approver=approver.name)
				self.add_comment("Created",comment)	
			if not self.p_id:
				frappe.throw(_("Please Select Project"))
			if not self.approver:
				frappe.throw(_("Please Select Approver"))	

		elif self.approval_required == 'No':
			"""
				send mail to executor
				if approver not required
			"""
			executor = self.get_executer_list()
			executor.append(self.requester_email_id)
			self.notify_user(executor,"Request Created","Request have only executer")
			self.allocated_to = "Executor"
			frappe.db.set_value("Request",self.name,"allocated_to","Executor")
			self.current_status = "Request Sent To Executor"
			frappe.db.set_value("Request",self.name,"current_status","Request Sent To Executor")
			for email in self.get_executer_names():
				self.share_document(email)
			self.share_document(self.requester_email_id)
			sreq = frappe.get_doc("Sub Request Category",self.sub_request_category) 
			comment = """Created Request and assigned to Executor : {role}""".format(role=sreq.executer)
			self.add_comment("Created",comment)

	def add_requetor_and_ticket_details_to_comment(self):
		comment = """Requestor and Ticket Details:\n
		Department: {dept}.\n
		Sub Request Category: {sub_req}.\n
		Subject: {subj}.\n
		Issue Desc: {desc}.\n""".format(dept=self.department_abbriviation,sub_req=self.sub_request_category,subj=self.subject,desc=self.issue_description)
		
		if self.approval_required == 'Yes': comment += """
		Project: {project}.\n
		Approver: {approver}.""".format(project=self.p_id,approver=self.approver)
		self.add_comment("Comment",comment)

	def add_requester_comments(self):
		comment = ''
		if(self.approver_status == "More Info Required"):
			comment = """Required Information For Approver:{required_info}:\n
		Requester Reply To Approver:{Approver}""".format(required_info=self.required_info,Approver=self.approver)
		
		elif(self.executor_status == "More information need"):
			comment = """Requester Reply To : Executor"""	
		self.add_comment("Comment",comment)	

	def add_executor_comments(self):
		comment = """Executor Details:\n
		Priority: {priority}.\n
		Due Date: {due_date}.\n
		Request Category: {r_cat}.\n
		Executor Status: {status}.\n""".format(priority=self.priority,due_date=self.due_date,r_cat=self.request_category,status=self.executor_status)
		
		self.add_comment("Comment",comment)

	def add_addn_approver_comments(self):
		comment = """Additional Approver Details:\n
		Addn-Approver Status: {status}.\n""".format(status=self.approver_status)
		
		if self.approver_status == 'Approved': 
			comment += """
		Addn-Approver's Comment: {comment}.\n""".format(comment=self.additional_approver_comments)
		
		elif self.approver_status == 'More Info Required':
			comment += """\n
		Addn-Approver's Comment: {comment}.\n""".format(comment=self.more_info)
		
		elif self.approver_status == 'Rejected':
			comment += """\n
		Addn-Approver's Comment: {comment}.\n""".format(comment=self.reason_of_rejection)
		
		self.add_comment("Comment",comment)

	def add_approver_comments(self):
		comment = """Approver Details:\n
		Approver Status: {status}.\n""".format(status=self.approver_status)
		
		if self.approver_status == 'Approved': 
			comment += """
		Approver's Comment: {comment}.\n""".format(comment=self.approver_comments)
		
		elif self.approver_status == 'More Info Required':
			comment += """\n
		Approver's Comment: {comment}.\n""".format(comment=self.more_information)
		
		elif self.approver_status == 'Rejected':
			comment += """\n
		Approver's Comment: {comment}.\n""".format(comment=self.reason_for_rejection)
		
		self.add_comment("Comment",comment)

	def perform_requester_operations(self):
		if(self.allocated_to == "Requester" and self.executor_status == "More information need"):
			self.allocated_to = "Executor"
			frappe.db.set_value("Request",self.name,"allocated_to","Executor")
			self.current_status = "Requester Sent Information To Executor"
			frappe.db.set_value("Request",self.name,"current_status","Requester Sent Information To Executor")
			self.editable_value = 4
			frappe.db.set_value("Request",self.name,"editable_value",4)
		
		elif(self.allocated_to == "Requester" and self.approver_status == "More Info Required"):
			self.allocated_to = "Approver"
			frappe.db.set_value("Request",self.name,"allocated_to","Approver")
			self.current_status = "Requester Sent Information To Approver"
			frappe.db.set_value("Request",self.name,"current_status","Requester Sent Information To Approver")
			self.editable_value = 1
			frappe.db.set_value("Request",self.name,"editable_value",1)
							
	def perform_approver_operations(self):
		executor = self.get_executer_list()
		executor.append(self.requester_email_id)
		if self.approver_status == 'Approved':
			self.notify_user(executor,"Request Approved","Request Approved by Approver")
			self.allocated_to = "Executor"
			frappe.db.set_value("Request",self.name,"allocated_to","Executor")
			self.current_status = "Approver Approved"
			frappe.db.set_value("Request",self.name,"current_status","Approver Approved")
			self.editable_value = 2
			frappe.db.set_value("Request",self.name,"editable_value",2)
			for email in self.get_executer_names():
				self.share_document(email)
			self.share_document(self.requester_email_id)
			sreq = frappe.get_doc("Sub Request Category",self.sub_request_category)
			comment = """approved the Request and assigned to Executor:{role}""".format(role=sreq.executer)
			self.add_comment("Approved",comment)

			#send notification to executor and requestor
		elif self.approver_status == 'More Info Required':
			#send notification to requestor
			self.notify_user(self.requester_email_id,"More Information","More Information Required")
			self.allocated_to = "Requester"
			frappe.db.set_value("Request",self.name,"allocated_to","Requester")
			self.current_status = "Approver Required More Information"
			frappe.db.set_value("Request",self.name,"current_status","Approver Required More Information")
			self.editable_value = 1
			frappe.db.set_value("Request",self.name,"editable_value",1)
			comment = """asked for More information from Requestor : {requestor}""".format(requestor=self.requester_email_id)
			self.add_comment("More Info",comment)
		
		elif self.approver_status == 'Rejected':
			#send notification to requestor
			self.notify_user(self.requester_email_id,"Rejection of Request","Request Rejected")
			self.current_status = "Approver Rejected"
			frappe.db.set_value("Request",self.name,"current_status","Approver Rejected")
			self.editable_value = 2
			frappe.db.set_value("Request",self.name,"editable_value",2)
			comment = """Has Rejected the request"""
			self.add_comment("Rejected",comment)
		
	
	def perform_executor_operations(self): 		
		if self.executor_status == "Pending From Requestor":
			if self.approver:
				approver = frappe.get_doc("Employee",self.approver)
				self.notify_user([self.requester_email_id,approver.user_id],"Request Pending","Request Pending On Requester Side")
				self.current_status = "Pending From Requester Side"
				frappe.db.set_value("Request",self.name,"current_status","Pending From Requester Side")
				comment = """Request status changed to by \"Pending From Requestor\" Executor"""
				self.add_comment(comment)
			self.notify_user(self.requester_email_id,"Request Pending","Request Pending On Requestor Side")
			self.current_status = "Pending From Requester Side"
			frappe.db.set_value("Request",self.name,"current_status","Pending From Requester Side")
			comment = """Request status changed to by \"Pending From Requestor\" Executor"""
			self.add_comment(comment)
		
		elif self.executor_status == "More information need":
			self.notify_user(self.requester_email_id,"More Information","More Information Required")
			self.allocated_to = "Requester"
			frappe.db.set_value("Request",self.name,"allocated_to","Requester")
			self.current_status = "Executor Required More Information"
			frappe.db.set_value("Request",self.name,"current_status","Executor Required More Information")
			self.editable_value = 4
			frappe.db.set_value("Request",self.name,"editable_value",4)
			comment = """asked for More information from Requestor : {requestor}""".format(requestor=self.requester_email_id)
			self.add_comment(comment)

		elif self.executor_status == "WIP":
			self.current_status = "Executor WIP"
			frappe.db.set_value("Request",self.name,"current_status","Executor WIP")

		elif self.executor_status == 'Additional Approver Required':
			if self.additional_approver:
				if self.more_information_required:
					self.notify_user([self.additional_approver],"Request for approval","Request Required Approval")
					self.allocated_to = "Ad Approver"
					frappe.db.set_value("Request",self.name,"allocated_to","Ad Approver")
					self.current_status = "Executor Sent Information To Ad-Approver"
					frappe.db.set_value("Request",self.name,"current_status","Executor Sent Information To Ad-Approver")
					self.editable_value = 3
					frappe.db.set_value("Request",self.name,"editable_value",3)
					self.share_document(self.additional_approver)
				else:
					self.notify_user([self.additional_approver],"Request for approval","Request Required Approval")
					self.allocated_to = "Ad Approver"
					frappe.db.set_value("Request",self.name,"allocated_to","Ad Approver")
					self.current_status = "Request Sent To Additional Approver"
					self.editable_value = 3
					frappe.db.set_value("Request",self.name,"editable_value",3)
					frappe.db.set_value("Request",self.name,"current_status","Request Sent To Additional Approver")
					self.share_document(self.additional_approver)			
			if not self.additional_approver:
				frappe.throw(_("Please Select Additional Approver"))	

		elif self.executor_status == "Resolved":
			self.notify_user(self.requester_email_id,"Resolved Request","Request Have Resolved")
			self.allocated_to = "Requester"
			frappe.db.set_value("Request",self.name,"allocated_to","Requester")
			self.current_status = "Executor Resolved"
			frappe.db.set_value("Request",self.name,"current_status","Executor Resolved")
			self.editable_value = 0
			frappe.db.set_value("Request",self.name,"editable_value",0)
			comment = """set the status as Resolved"""
			self.add_comment(comment)
			
		#elif self.additional_approver_status == "More Info Required" and current_status == "Additional Approver Required More Information":	
			# self.editable_value = 3
			# frappe.db.set_value("Request",self.name,"editable_value",3)			

	def perform_additional_approver_operations(self):
		executor = self.get_executer_list()
		executor.append(self.requester_email_id)		
		
		if self.additional_approver_status == "Approved":
			self.notify_user(executor,"Request Approved","Request Approved By Additional Approver")
			self.allocated_to = "Executor"
			frappe.db.set_value("Request",self.name,"allocated_to","Executor")
			self.current_status = "Additional Approver Approved"
			frappe.db.set_value("Request",self.name,"current_status","Additional Approver Approved")
			self.editable_value = 4
			frappe.db.set_value("Request",self.name,"editable_value",4)
			comment = """ Approved""".format(user=frappe.session.user)
			self.add_comment(comment)
		
		elif self.additional_approver_status == "More Info Required":
			self.notify_user(executor,"More Information","More Information Required")
			self.allocated_to = "Executor"
			frappe.db.set_value("Request",self.name,"allocated_to","Executor")
			self.current_status = "Additional Approver Required More Information"
			frappe.db.set_value("Request",self.name,"current_status","Additional Approver Required More Information")
			self.editable_value = 4
			frappe.db.set_value("Request",self.name,"editable_value",4)	
			comment = """ asked for More information from Executor""".format(user=frappe.session.user)
			self.add_comment(comment)
		
		elif self.additional_approver_status == "Rejected":
			self.notify_user(executor,"Rejection of Request","Request Rejected")
			self.allocated_to = "Executor"
			frappe.db.set_value("Request",self.name,"allocated_to","Executor")
			self.current_status = "Additional Approver Rejected"
			frappe.db.set_value("Request",self.name,"current_status","Additional Approver Rejected")
			self.editable_value = 4
			frappe.db.set_value("Request",self.name,"editable_value",4)			
			comment = """ Rejected""".format(user=frappe.session.user,requestor=self.requester_email_id)
			self.add_comment(comment)

	def notify_user(self,receiver,subj,msg):
		"""
			send mail notification
		"""	
		frappe.sendmail(receiver, subject=subj, message =msg)


	def get_executer_list(self):
		if(self.approver):
			approver = frappe.get_doc("Employee",self.approver)
			list0 = [self.requester_email_id,approver.user_id]
			list1 = tuple([x.encode('UTF8') for x in list0 if x])
			sreq = frappe.get_doc("Sub Request Category",self.sub_request_category)
			user_list = frappe.db.sql("""select t1.email from `tabUser` t1,`tabUserRole` t2 
				where t1.name = t2.parent and t2.role = '{0}' and t1.email not in {1} """.format(sreq.executer,list1),as_list =1)
		 	if(user_list == []):
	 			frappe.throw(_("For This Sub Reueqst Category No One have role of {0} As Executor ,Please Give Any User To The Role Of {0}")
				.format(sreq.executer))
		 	chain = itertools.chain(*user_list)
		 	return list(chain)
		else:
			list0 = [x.encode('UTF8') for x in [self.requester_email_id] if x]
			list1 = list0[0]
			sreq = frappe.get_doc("Sub Request Category",self.sub_request_category)
			user_list = frappe.db.sql("""select t1.email from `tabUser` t1,`tabUserRole` t2 
			where t1.name = t2.parent and t2.role = '{0}' and t1.email <> '{1}' """.format(sreq.executer,list1),as_list =1)
	 		print user_list
	 		if(user_list == []):
	 			frappe.throw(_("For This Sub Reueqst Category No One have role of {0} As Executor ,Please Give Any User To The Role Of {0}")
				.format(sreq.executer))
	 		chain = itertools.chain(*user_list)
	 		return list(chain)
		

	def get_executer_names(self):
		sreq = frappe.get_doc("Sub Request Category",self.sub_request_category)
		user_list = frappe.db.sql("""select t1.name from `tabUser` t1,`tabUserRole` t2 
			where t1.name = t2.parent and t2.role = '{0}'""".format(sreq.executer),as_list =1)
	 	chain = itertools.chain(*user_list)
	 	return list(chain)


	def share_document(self,user):
		"""
			assign document to approver,executor or add approver depending on conditions.

		"""
		frappe.share.add("Request",self.name,user,read=1,write=1,share=1,flags={"ignore_share_permission": True})

	def add_comment_to_doc(self,comment):
		frappe.get_doc({
			"doctype":"Comment",
			"comment_by": frappe.session.user,
			"comment_doctype": self.doctype,
			"comment_docname": self.name,
			"comment": comment
		}).insert(ignore_permissions=True)

	def add_comments_for_additional_activities(self):
		if self.allocated_to == 'Approver' and self.approver_status == 'More Info Required':
			pass

		elif self.allocated_to == 'Executor':
			self.perform_executor_operations()
		elif self.allocated_to == 'Ad Approver':
			self.perform_additional_approver_operations()	

	def close_request(self):
		if self.request_status == "Close":
			self.current_status = "Request Closed"
			frappe.db.set_value("Request",self.name,"current_status","Request Closed")

@frappe.whitelist()
def get_user_details():
	current_user = frappe.get_doc("User",frappe.session.user)
	cell = frappe.db.get_value("Employee",{"user_id":current_user.name},"cell_number")
	return {'requester_name':current_user.first_name,'email':current_user.email,'cell_number':cell}
	
def get_holiday(due_date):
	tot_hol = frappe.db.sql("""select count(*) from `tabHoliday List` h1,`tabHoliday` h2 
	where h2.parent = h1.name and h1.name = 'Mycfo' and h2.holiday_date >= %s and  h2.holiday_date <= %s""",(nowdate(),due_date.strftime("%Y-%m-%d")))
	return tot_hol[0][0]

@frappe.whitelist()
def get_due_date(doc):
	doc = json.loads(doc)
	tat = frappe.db.get_value("TAT", {"priority":doc.get('priority')}, "tat")
	due_date = datetime.now() + timedelta(hours=tat)
	holiday	= get_holiday(due_date)
	tat_with_holiday = holiday*24 + tat
	due_date_with_holiday = datetime.now() + timedelta(hours=tat_with_holiday)
	return due_date_with_holiday.strftime("%Y-%m-%d")

def get_executer_list(doc):
	emp_user=''
	doc['approver'] = ''
	if doc['approver']:
		emp_user = frappe.db.get_value("Employee",doc['approver'],"user_id")
		list0 = [doc['requester_email_id'],emp_user]
		list1 = tuple([x.encode('UTF8') for x in list0 if x])
		sreq = frappe.get_doc("Sub Request Category",doc.get('sub_request_category'))
		user_list = frappe.db.sql("""select t1.email from `tabUser` t1,`tabUserRole` t2 
		where t1.name = t2.parent and t2.role = '{0}' and t1.email not in {1}""".format(sreq.executer,list1),as_list =1)
		chain = itertools.chain(*user_list)
		list_users = list(chain)
 		return list_users	
	else:
		list1 = (doc['requester_email_id'])
		sreq = frappe.get_doc("Sub Request Category",doc.get('sub_request_category'))
		user_list = frappe.db.sql("""select t1.email from `tabUser` t1,`tabUserRole` t2 
		where t1.name = t2.parent and t2.role = '{0}' and t1.email <> '{1}' """.format(sreq.executer,list1),as_list =1)
 		chain = itertools.chain(*user_list)
 		list_users = list(chain)
 		return list_users
	
@frappe.whitelist()	
def check_for(check_for,doc):
	current_doc = json.loads(doc)
	current_user = frappe.session.user
	if check_for == 'Approver' and current_doc.get('approver'):
		emp_user = frappe.db.get_value("Employee",current_doc.get('approver'),"user_id")
	if check_for == 'Requester' and current_doc.get('requester_email_id') != current_user:
		return "Not Allowed Only Requester Can edit these fields"
	if check_for == 'Approver' and emp_user != current_user:
		return "Not Allowed only approver can edit these fields"	 
	if check_for == 'Executor' and current_user not in get_executer_list(current_doc):
		return "Not Allowed only executor can edit these fields"
	if check_for == 'Additional Approver' and current_doc.get('additional_approver') != current_user:
		return "Not Allowed only additional_approver can edit these fields"

	 

def get_approver_list(doctype, txt, searchfield, start, page_len, filters):
	op_and_project = frappe.db.sql("""select name from `tabOperation And Project Commercial`
		where project_commercial = %s""",(filters.get("project_id")),as_list =1)
	new_op_and_project = [op[0] for op in op_and_project if op]
	new = ','.join('"{0}"'.format(w) for w in new_op_and_project)
	approver = frappe.db.sql("""select name,employee_name from `tabEmployee` where name in
					( select Distinct user_name from `tabOperation And Project Details`t1
					where t1.parent in ({0})) and user_id <> %s """.format(new),filters['doc']['requester_email_id'],as_list=1)
	# approver = frappe.db.sql("""select name,employee_name from `tabEmployee` where name in
	# 				( select Distinct user_name from `tabOperation And Project Details`t1
	# 				where t1.parent in ({0}) and t1.role = "EL" or t1.role = "EM") """.format(new),as_list=1)
	return approver

# def generate_support_id(source_name):
# 	count = frappe.get_value("Request",source_name,"incre") + 1
# 	support_id = source_name +'-'+cstr(count)
# 	frappe.db.set_value("Request",source_name,"incre",count)
# 	return support_id

@frappe.whitelist()
def status_permission(doc):
	current_doc = json.loads(doc)
	emp_user=''
	executor=''
	if current_doc.get('approver'):
		emp_user = frappe.db.get_value("Employee",current_doc.get('approver'),"user_id")
	
	if frappe.session.user == emp_user:
		return {'valid':'true','Existing_user':'Approver'}	
	
	if current_doc.get('sub_request_category'):
		executor = get_executer_list(current_doc)
	
	if frappe.session.user in executor:
		return {'valid':'true','Existing_user':'Executor'}
	
	elif frappe.session.user == current_doc.get('additional_approver'):
		return {'valid':'true','Existing_user':'Ad_Approver'}
	
	elif frappe.session.user:
		return {'valid': 'true','Existing_user': 'Requester'}		
	else:
		return {'valid':'false'}			

@frappe.whitelist()		
def check_pc_exists(doc):
	doc = json.loads(doc)
	op_and_project = frappe.db.sql("""select name from `tabOperation And Project Commercial`
		where project_commercial = %s""",(doc.get("p_id")),as_list =1)
	if op_and_project:
		return True
	else:
		return False

def get_permission_query_conditions(user):
	if not user: user = frappe.session.user
	"""
		get all shared documents from shared doc list
		see the names in current doc
	"""
	#pass
	if not user == 'Administrator':
		documents = frappe.db.sql("""select share_name from 
			`tabDocShare` where user=%s and share_doctype="Request" """,user,as_dict=1)
		doc_list = "', '".join([doc.share_name for doc in documents if documents])
		return """(`tabRequest`.name in ('{doc_list}'))""".format(doc_list=doc_list)


@frappe.whitelist()
def filter_employee(doctype, txt, searchfield, start, page_len, filters):
	emp_name = frappe.db.sql("""select name,employee_name from `tabEmployee` where user_id != %s""",frappe.session.user,as_list=1)
	return emp_name	

@frappe.whitelist()
def filter_ad_approver(doctype, txt, searchfield, start, page_len, filters):
	emp_user=''
	executor=''
	if filters['doc']['approval_required'] == "Yes":
		emp_user = frappe.db.get_value("Employee",filters['doc']['approver'],"user_id")
	if filters['doc']['sub_request_category']:
		sreq = frappe.get_doc("Sub Request Category",filters['doc']['sub_request_category'])
		user_list = frappe.db.sql("""select t1.email from `tabUser` t1,`tabUserRole` t2 
		where t1.name = t2.parent and t2.role = '{0}'""".format(sreq.executer),as_list =1)
	 	chain = itertools.chain(*user_list)
 		executor = list(chain)
	list1 = [filters['doc']['requester_email_id'],emp_user]
	chain = itertools.chain(executor,list1)
	list2 = tuple([x.encode('UTF8') for x in list(chain) if x])
 	ad_approver	= frappe.db.sql("""select email,first_name,last_name from `tabUser` where email not in {0}""".format(list2),as_list=1)
 	return ad_approver