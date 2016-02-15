import frappe

def get_total_request_generated(start, end):
	filters = [["Request", "creation", ">=", start],["Request", "creation", "<=", end]]
	fields = ["count(request_status) as count", "request_status", "department_abbriviation"]
	try:
		results = frappe.get_all("Request", fields=fields, filters=filters, group_by="request_status,department_abbriviation")
		return prepare_data(results)
	except Exception, e:
		return None

def prepare_data(results):
	if not results:
		return None

	data = []
	requests = {}
	total_tickets = 0
	total_open = 0
	total_closed = 0
	total_pending = 0

	for record in results:
		status = record.get("request_status")
		count = int(record.get("count"))
		dept = record.get("department_abbriviation")

		if requests.get(dept):
			requests.get(dept).update({ status:count })
		else:
			requests.update({ dept: { status:count } })

		total_tickets += count
		if status == "Open":
			total_open += count
		elif status == "Close":
			total_closed += count
		else:
			total_pending += count
	frappe.errprint(results)
	data = [["Genre", "Open", "Pending", "Closed", { "role": "annotation" }]]
	chart_data = [[key, request.get("Open") or 0, request.get("Pending") or 0, request.get("Close") or 0, ""] \
		for key, request in requests.iteritems()]
	data.extend(chart_data)
	data.append(["Total", total_open, total_pending, total_closed, ""])

	return {
		"requests": data,
		"table": list(zip(*data)),
	}