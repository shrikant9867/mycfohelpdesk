import frappe
from frappe.utils import time_diff_in_hours

@frappe.whitelist()
def get_tat_for_closed_ticket(start, end):
	filters = [
		["Request", "start_date", ">=", start],
		["Request", "start_date", "<=", end],
		["Request", "end_date", ">=", start],
		["Request", "end_date", "<=", end],
		["Request", "request_status","=","Close"]
	]

	fields = [
		"end_date",
		"start_date",
		"department_abbriviation"
	]

	results = frappe.get_all("Request", fields=fields, filters=filters)

	return prepare_data(results)

def get_leagend(start, end):
	time_diff = time_diff_in_hours(end, start)
	if time_diff <= 24.0:
		return "Winthin 1 day"
	elif time_diff <= 72.0:
		return "2-3 days"
	elif time_diff <= 120.0:
		return "3-5 days"
	elif time_diff <= 168.0:
		return "5-7 days"
	else:
		return "more than 7 days"

def prepare_data(results):
	"""results = [{
			'department_abbriviation': u'ACC',
			'end_date': datetime.datetime(2016, 2, 10, 15, 27, 46),
			'start_date': datetime.datetime(2016, 2, 10, 14, 38, 7, 34947)
		}]"""
	if not results:
		return None

	data = []
	requests = {}
	
	total_tickets = 0
	within_day = 0
	two_three_days = 0
	three_five_days = 0
	five_seven_days = 0
	more_than_seven = 0

	for record in results:
		dept = record.get("department_abbriviation")
		closed_in = get_leagend(record.get("start_date"), record.get("end_date"))
		count = 1

		if requests.get(dept):
			rec = requests.get(dept)
			count = rec.get(closed_in) + 1 if rec.get(closed_in) else 1
			requests.get(dept).update({ closed_in:count })
		else:
			requests.update({ dept: { closed_in:count } })

		total_tickets += count
		if closed_in == "Winthin 1 day":
			within_day += count
		elif closed_in == "2-3 days":
			two_three_days += count
		elif closed_in == "3-5 days":
			three_five_days += count
		elif closed_in == "5-7 days":
			five_seven_days += count
		else:
			more_than_seven += count

	data = [["Genre", "Winthin 1 day", "2-3 days", "3-5 days", "5-7 days", "more than 7 days", { "role": "annotation" }]]
	chart_data = [[key, request.get("Winthin 1 day") or 0, request.get("2-3 days") or 0, request.get("3-5 days") or 0, \
		request.get("5-7 days") or 0, request.get("more than 7 days") or 0, ""] for key, request in requests.iteritems()]
	data.extend(chart_data)
	data.append(["Total", within_day, two_three_days, three_five_days, five_seven_days, more_than_seven, ""])

	return {
		"requests": data,
		"table": list(zip(*data)),
	}