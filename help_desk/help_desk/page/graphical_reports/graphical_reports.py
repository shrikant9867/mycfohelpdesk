import frappe
from help_desk.reports import (get_tat_for_closed_ticket, get_total_request_generated, get_db_count_for_industry_document,
								get_pending_file_for_approval, get_upload_trends, get_download_trends, get_user_wise_upload_trends,
								get_user_wise_download_trends)

reports_mapper = {
	"tat-closed-tickets": get_tat_for_closed_ticket,
	"total-request-generated": get_total_request_generated,
	"industry-document-type": get_db_count_for_industry_document,
	"pending-files-industry": get_pending_file_for_approval,
	"upload-trends": get_upload_trends,
	"download-trends": get_download_trends,
	"user-upload-trend":get_user_wise_upload_trends,
	"user-download-trend": get_user_wise_download_trends,
}

@frappe.whitelist()
def get(start, end, report):
	return reports_mapper[report](start, end)