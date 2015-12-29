# -*- coding: utf-8 -*-
# Copyright (c) 2015, Indictrans and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
import string
from frappe.model.document import Document
from frappe.utils import cstr, flt, getdate, comma_and, cint
from frappe import _
from erpnext.controllers.item_variant import get_variant, copy_attributes_to_variant, ItemVariantExistsError

class DepartmentName(Document):
	
	def autoname(self):
		self.name = self.department_abbriviation.upper()

	def validate(self):
		self.validate_name_of_department()

	def validate_name_of_department(self):
		if(self.name_of_department):
			self.name_of_department = self.name_of_department.title()
		if(self.department_abbriviation):
			self.department_abbriviation = self.department_abbriviation.upper()										