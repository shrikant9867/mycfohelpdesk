import frappe

def get_upload_trends(start, end, user_wise=False):
	fields = ["DATE_FORMAT(creation,'%d-%m-%y') as date"] if not user_wise else ["owner as user"]
	fields.append("count(name) as count")

	filters = [
		["IP File", "creation", ">=", start],
		["IP File", "creation", "<=", end],
	]

	group_by = "DATE_FORMAT(creation,'%d-%m-%y')" if not user_wise else "owner"

	try:
		requests = [['Date', 'Upload Trends']] if not user_wise else [['User', 'Upload Trends']]
		results = frappe.get_all("IP File", fields=fields, filters=filters, group_by=group_by, as_list=True)
		requests.extend([list(result) for result in results])
		return {
			'requests': requests,
		}
	except Exception, e:
		return None

def get_user_wise_upload_trends(start, end):
	return get_upload_trends(start, end, user_wise=True)