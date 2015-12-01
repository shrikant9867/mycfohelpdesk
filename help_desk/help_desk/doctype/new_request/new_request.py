# -*- coding: utf-8 -*-
# Copyright (c) 2015, Indictrans and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, flt, getdate, comma_and, cint
from frappe.model.naming import make_autoname
from frappe import throw, _
from frappe.model.document import Document
from erpnext.controllers.item_variant import get_variant, copy_attributes_to_variant, ItemVariantExistsError

class NewRequest(Document):
	

	# def autoname(self):
	# 	self.name = self.d_abb.strip() + ' - ' + \
	# 		frappe.db.get_value("Department Name", self.d_abb, "d_abb")
	# print "hello"

	# def autoname(self):
	# 	s_id = 1
	# 	for s_id in range(1000):
	# 		self.name = frappe.db.get_value("Department Name", self.d_abb, "d_abb") + ' - ' + \
	# 				self.s_id

	
# frappe.msgprint("%s created successfully",project.project_name)

	def autoname(self):
		if self.status == "Open":
			self.name = make_autoname(self.d_abb.upper()+ ' - ' +'.#####')   	
		# self.s_id = self.name
		elif self.status == "Reopen":
			print"Reopen"
			self.name.replace("self.name","self.s_id")
			# self.name = make_autoname(self.d_abb.upper()+ ' - ' +'.#####'+ '-' + str(self.incre))
			# self.incre = self.incre + 1

	def validate(self):	
		self.validate_status()

	def validate_status(self):
		if self.status == "Open":
			self.s_id = self.name
			# self.status = "Reopen"
		# elif self.status == "Reopen":
			print"hello"
			print type(self.incre)
		elif self.status == "Reopen":	   
			self.s_id = self.name + '-' + str(self.incre) 
			self.incre = self.incre + 1
	


@frappe.whitelist()
def make_self_entry():
	print frappe.session.user
	return frappe.db.sql("""select first_name,email,requester_contact_number from `tabUser` where name = '{0}'""".format(frappe.session.user),as_list = 1)
	# return frappe.db.sql("""select cell_number from `tabEmployee` where user_id ='{0}'""".format(frappe.session.employee),as_dict = 1)	
				




