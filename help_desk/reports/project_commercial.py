import frappe
from frappe.utils import flt

def get_project_commercial_report(start, end):
	query = """SELECT c.customer as cust, sum(c.p_value) as total, group_concat(c.name) as projects,
				group_concat(c.p_value) as val, ( SELECT count(a.email_id)
	    		FROM `tabOperation And Project Details` AS a
	    		LEFT JOIN `tabOperation And Project Commercial` AS b
	    		ON 
    	    		a.parent=b.name
    			WHERE
        			b.customer=c.customer) AS head_count
			FROM `tabProject Commercial` AS c
			GROUP BY  c.customer"""

	result = frappe.db.sql(query, as_dict=True)
	return prepare_data(result)

def prepare_data(results):
	if not results:
		return None

	data = [["User", "Project Value", "Average Cost", "Head Count"]]

	for record in results:
		customer = record.get("cust")
		total = record.get("total")
		head_count = int(record.get("head_count"))
		data.append([customer, total, flt(total/head_count, 2), head_count])

	return {
		'requests': data,
		'table': list(zip(*data))
	}