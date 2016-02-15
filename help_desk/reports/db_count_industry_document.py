import frappe

def get_db_count_for_industry_document(start, end):
	fields = [
		"industry",
		"document_type",
		"count(name) as count"
	]

	try:
		results = frappe.get_all("Request", fields=fields, filters=None, group_by="industry, document_type")
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
		document_type = record.get("document_type")
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