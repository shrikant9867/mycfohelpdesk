import frappe

def get_download_trends(start, end, user_wise=False):
	fields = ["DATE_FORMAT(creation,'%d-%m-%y') as date"] if not user_wise else ["full_name as user"]
	fields.append("count(name) as count")

	filters = [
		["IP Download Log", "creation", ">=", start],
		["IP Download Log", "creation", "<=", end],
	]

	group_by = "DATE_FORMAT(creation,'%d-%m-%y')" if not user_wise else "user_id"

	try:
		requests = [['Date', 'Download Trends']] if not user_wise else [['User', 'Download Trends']]
		results = frappe.get_all("IP Download Log", fields=fields, filters=filters, group_by=group_by, as_list=True)
		requests.extend([list(result) for result in results])
		return {
			'requests': requests,
		}
	except Exception, e:
		return None

def get_user_wise_download_trends(start, end):
	return get_download_trends(start, end, user_wise=True)