import frappe



def get_training_distribution_data(start, end):
	result = frappe.db.sql(""" select skill_matrix_18, count(name) 
									from `tabTraining` group by skill_matrix_18 """, as_list=1)
	result_list = [["Skill Matrix 18", "Total Count"]]
	result_list.extend([ list(row) for row in result ])
	return { "requests":  result_list }


def get_discussion_forum_data(start, end):
	result = frappe.db.sql(""" select blog_category, count(name) 
									from `tabDiscussion Topic` group by blog_category """, as_list=1)
	result_list = [["Discussion Topic Category", "Total Count"]]
	result_list.extend([ list(row) for row in result ])
	return { "requests":  result_list }	