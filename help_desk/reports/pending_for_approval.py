import frappe

def get_pending_file_for_approval(start, end):
	fields = [
		"industry",
		"file_type",
		"count(name) as count"
	]

	filters = [["IP Approver", "current_status", "in", ["Open", "Approved by Approver", "Rejected by Approver"]]]

	try:
		results = frappe.get_all("IP Approver", fields=fields, filters=filters, group_by="industry, file_type")
		return prepare_data(results)
	except Exception, e:
		return None

def prepare_data(results):
	if not results:
		return None

	data = []
	legends = []
	totals = {}
	requests = {}

	for record in results:
		industry = record.get("industry")
		count = int(record.get("count"))
		document_type = record.get("file_type")
		if document_type not in legends: legends.append(document_type)

		if requests.get(industry):
			requests.get(industry).update({ document_type:count })
		else:
			requests.update({ industry: { document_type:count } })

		count += totals.get(document_type) or 0
		totals.update({document_type: count})

	legends = list(set(legends))
	legends.sort()
	legends = ["Genre"] + legends
	legends.append({ "role": "annotation" })

	data = [legends]
	for key, value in requests.iteritems():
		chart_data = []
		chart_data.extend([key] + [value.get(genre) or 0 for genre in legends[1:-1]] + [""])
		data.append(chart_data)

	data = [legends]
	for key in sorted(requests):
		chart_data = []
		chart_data.extend([key] + [requests.get(key).get(genre) or 0 for genre in legends[1:-1]] + [""])
		data.append(chart_data)

	data.append(["Total"] + [totals.get(genre) or 0 for genre in legends[1:-1]] + [""])

	return {
		"requests": data,
		"table": list(zip(*data)),
	}