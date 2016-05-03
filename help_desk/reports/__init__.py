import frappe

from tat_closed_ticket import get_tat_for_closed_ticket
from total_request_generated import get_total_request_generated
from db_count_industry_document import get_db_count_for_industry_document
from pending_for_approval import get_pending_file_for_approval
from upload_trends import get_upload_trends, get_user_wise_upload_trends, get_ip_file_distribution_data
from download_trends import get_download_trends, get_user_wise_download_trends
from project_commercial import get_project_commercial_report
from project_commercial import get_project_commercial_report
from training_reports import get_training_distribution_data, get_discussion_forum_data


reports_mapper = {
	"tat-closed-tickets": get_tat_for_closed_ticket,
	"total-request-generated": get_total_request_generated,
	"industry-document-type": get_db_count_for_industry_document,
	"pending-files-industry": get_pending_file_for_approval,
	"upload-trends": get_upload_trends,
	"download-trends": get_download_trends,
	"user-upload-trend":get_user_wise_upload_trends,
	"user-download-trend": get_user_wise_download_trends,
	"project-commercial-report": get_project_commercial_report,
	"ip-file-distribution":get_ip_file_distribution_data,
	"training-distribution":get_training_distribution_data,
	"discussion-topic":get_discussion_forum_data
}

@frappe.whitelist()
def get(start, end, report):
	return reports_mapper[report](start, end)