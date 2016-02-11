import frappe
from help_desk.reports import (get_tat_for_closed_ticket, get_total_request_generated)

reports_mapper = {
	"tat-closed-tickets": get_tat_for_closed_ticket,
	"total-request-generated": get_total_request_generated
}

@frappe.whitelist()
def get(start, end, report):
	return reports_mapper[report](start, end)