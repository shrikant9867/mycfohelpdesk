# -*- coding: utf-8 -*-
# Copyright (c) 2015, Indictrans and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import itertools
import json
from frappe.utils import get_link_to_form,get_url_to_form,comma_or,get_fullname,nowdate, getdate
from frappe.model.naming import make_autoname
from frappe import throw, _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe import msgprint
from frappe.utils import now_datetime
from datetime import datetime, timedelta

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
			self.name = make_autoname(self.department_abbriviation.upper()+ ' - ' +'.#####')

	def validate(self):	
		self.validate_status()

	def on_update(self):
		self.build_notification()

	def build_notification(self):
		"""
			Decide whom to notify
		"""
		if self.allocated_to == '':
			self.notify_to_approver_or_executor()
		elif self.allocated_to == 'Approver':
			self.perform_approver_operations()
		elif self.allocated_to == 'Executor':
			self.perform_executor_operations()
		elif self.allocated_to == 'Ad Approver':
			self.perform_additional_approver_operations()	

	def notify_to_approver_or_executor(self):
		"""
			if subrequest has approver then send notification to approver else send notification to executer 
			after sending mail change status of allocated_to to approver or executer
		"""
		print "in notify_to_approver_or_executor"
		if self.approval_required == 'Yes':
			"""
				send mail to approver and requestor
				["approver@gmail.com","requestor@gmail.com"]
			"""
			# approver = frappe.get_doc("User",self.approver)
			approver = frappe.get_doc("Employee",self.approver)
			self.notify_user([approver.user_id,self.requester_email_id],"Request Created","Request has been created")
			self.allocated_to = "Approver"
			frappe.db.set_value("Request",self.name,"allocated_to","Approver")
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

	
	def perform_approver_operations(self):
		print "perform_approver_operations"
		executor = self.get_executer_list()
		executor.append(self.requester_email_id)
		if self.approver_status == 'Approved':
			self.notify_user(executor,"Request Approved","Request Approved by Approver")
			self.allocated_to = "Executor"
			frappe.db.set_value("Request",self.name,"allocated_to","Executor")
			#send notification to executor and requestor
		elif self.approver_status == 'More Info Required':
			#send notification to requestor
			self.notify_user(self.requester_email_id,"More Information","More Information Required")
		elif self.approver_status == 'Rejected':
			#send notification to requestor
			self.notify_user(self.requester_email_id,"Rejection of Request","Request Rejected")
	
	def perform_executor_operations(self): 		
		if self.executor_status == "Pending From Requestor":
			approver = frappe.get_doc("User",self.approver)
			self.notify_user([self.requester_email_id,approver.email],"Request Pending","Request Pending On Requestor Side")
		
		elif self.executor_status == "More information need":
			self.notify_user(self.requester_email_id,"More Information","More Information Required")
		
		elif self.executor_status == "Resolved":
			self.notify_user(self.requester_email_id,"Resolved Request","Request Have Resolved")

		if self.additional_approval_required == 'Yes':
			self.notify_user([self.additional_approver],"Request for approval","Request Required Approval")
			self.allocated_to = "Ad Approver"
			frappe.db.set_value("Request",self.name,"allocated_to","Ad Approver")	

	def perform_additional_approver_operations(self):
		executor = self.get_executer_list()
		executor.append(self.requester_email_id)		
		
		if self.additional_approver_status == "Approved":
			self.notify_user(executor,"Request Approved","Request Approved By Additional Approver")
		
		elif self.additional_approver_status == "More Info Required":
			self.notify_user(executor,"More Information","More Information Required")
		
		elif self.additional_approver_status == "Rejected":
			self.notify_user(executor,"Rejection of Request","Request Rejected")			
			
	def notify_user(self,receiver,subj,msg):
		"""
			send mail notification
		"""	
		frappe.sendmail(receiver, subject=subj, message =msg)

	def get_executer_list(self):
		sreq = frappe.get_doc("Sub Request Category",self.sub_request_category)
		user_list = frappe.db.sql("""select t1.email from `tabUser` t1,`tabUserRole` t2 
			where t1.name = t2.parent and t2.role = '{0}'""".format(sreq.executer),as_list =1)
	 	chain = itertools.chain(*user_list)
	 	return list(chain)	

	def assign(self):
		"""
			-check whether there is to assigned for these doc if yes change the name of owne	
		"""
	def validate_approver_list(self):
		# operational_id = frappe.db.sql("""select operational_id from `tabOperation And Project Commercial`t1,
		# 			`tabProject Commercial`t2 where t1.project_commercial = t2.p_id;""",as_list =1)
		# new_operational_id = [op[0] for op in operational_id if op] 	
		# new = ','.join('"{0}"'.format(w) for w in new_operational_id)
		# approver = frappe.db.sql("""select name from `tabEmployee` where name in
		# 				(select user_name from `tabOperation Details`t1
		# 				where t1.parent = %s and t1.role = "EL" or t1.role = "EM")""",(new),as_list=1)
		# print new
		# print approver
		self.name = self.support_id
		print self.support_id
@frappe.whitelist()
def get_user_details():
	return frappe.get_doc("User",frappe.session.user)


def get_holiday(due_date):
	# print nowdate()
	# print getdate()
	tot_hol = frappe.db.sql("""select count(*) from `tabHoliday List` h1,`tabHoliday` h2 
	where h2.parent = h1.name and h1.name = 'Mycfo' and h2.holiday_date >= %s and  h2.holiday_date <= %s""",(nowdate(),due_date.strftime("%Y-%m-%d")),debug =True)
	# print tot_hol[0][0]
	return tot_hol[0][0]

@frappe.whitelist()
def get_due_date(doc):
	doc = json.loads(doc)
	tat = frappe.db.get_value("TAT", {"priority":doc.get('priority')}, "tat")
	# print d.strftime("%Y-%m-%d")
	due_date = datetime.now() + timedelta(hours=tat)
	holiday	= get_holiday(due_date)
	tat_with_holiday = holiday*24 + tat - 24
	print tat_with_holiday
	# print e.strftime("%Y-%m-%d")
	due_date_with_holiday = datetime.now() + timedelta(hours=tat_with_holiday)
	return due_date_with_holiday.strftime("%D")

def get_executer_list(doc):
	sreq = frappe.get_doc("Sub Request Category",doc.get('sub_request_category'))
	user_list = frappe.db.sql("""select t1.email from `tabUser` t1,`tabUserRole` t2 
		where t1.name = t2.parent and t2.role = '{0}'""".format(sreq.executer),as_list =1)
 	chain = itertools.chain(*user_list)
 	return list(chain)
	

@frappe.whitelist()	
def check_for(check_for,doc):
	current_doc = json.loads(doc)
	print current_doc
	current_user = frappe.session.user
	# print current_user
	if check_for == 'Requester' and current_doc.get('requester_email_id') != current_user:
		return "Not Allowed only Requester can Edit this field"
	if check_for == 'Approver' and current_doc.get('approver') != current_user:
		return "Not Allowed only approver can edit these fields" 
	if check_for == 'Executor' and current_user not in get_executer_list(current_doc):
		print get_executer_list(current_doc)
		return "Not Allowed only executor can edit these fields"
	if check_for == 'Additional Approver' and current_doc.get('additional_approver') != current_user:
		return "Not Allowed only additional_approver can edit these fields"
	 
@frappe.whitelist()
def get_approver_list(doc):
	project_doc = json.loads(doc)
	op_and_project = frappe.db.sql("""select name from `tabOperation And Project Commercial`
		where project_commercial = %s""",(project_doc.get("p_id")),as_list =1,debug =True)
	new_op_and_project = [op[0] for op in op_and_project if op]
	new = ','.join('"{0}"'.format(w) for w in new_op_and_project)
	approver = frappe.db.sql("""select name from `tabEmployee` where name in
					(select user_name from `tabOperation And Project Details`t1
					where t1.parent = %s and t1.role = "EL" or t1.role = "EM")""",(new),as_list=1,debug =True)
	return approver

@frappe.whitelist()
def make_new_request(source_name, target_doc=None):
	
	def refresh_values(source, target):
		target.subject = ""
		target.department_abbriviation = ""
		target.sub_request_category = ""
		target.approval_required = ""
		target.issue_description = ""
		target.p_id = ""
		target.approver = ""
		target.request_status = "Open"
	doclist = get_mapped_doc("Request",source_name,{
		"Request": {
		"doctype": "Request",
		#  "field_map":{
		#  "on_the_behalf_of":"on_the_behalf_of"
		# }
		}
		}, target_doc, refresh_values)
	return doclist
