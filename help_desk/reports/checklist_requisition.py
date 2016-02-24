import frappe
from frappe.utils import time_diff_in_hours

def get_total_request_generated(start, end):
	filters = [["Checklist Requisition", "creation", ">=", start],["Checklist Requisition", "creation", "<=", end]]
	fields = ["count(checklist_status) as count", "checklist_status", "checklist_name"]
	try:
		results = frappe.get_all("Checklist Requisition", fields=fields, filters=filters, group_by="checklist_status,checklist_name")
		return prepare_data(results)
	except Exception, e:
		return None

def prepare_data(results):
	if not results:
		return None

	return None