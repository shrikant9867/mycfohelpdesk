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


def get_discussion_topics_commented_data(start, end):
	result = frappe.db.sql(""" select dt.blog_category, dt.name, 
									( select count(*) from `tabComment` where comment_doctype = "Discussion Topic" and comment_docname = dt.name and comment_type = "Comment" ) as comment_count 
									from `tabDiscussion Topic` dt """, as_dict=1)
	category_list = frappe.db.sql(""" select blog_category, count(name) as topic_count 
									from `tabDiscussion Topic` group by blog_category """, as_dict=1)
	result_list = [["Discussion Category", "Attended", "Un-Attended", { "role": "annotation" }]]
	data_list = get_formatted_result(category_list, result)
	result_list.extend(data_list)
	return { "requests":  result_list }


def get_formatted_result(category_list, result):
	my_list = []
	for row in category_list:
		new_list = []
		commented_topic_count = len(filter(lambda topic: topic.get("blog_category") == row.get("blog_category") and topic.get("comment_count") > 0, result))
		new_list = [row.get("blog_category"), commented_topic_count, row.get("topic_count",0) - commented_topic_count, row.get("topic_count",0)]
		my_list.append(new_list)
	return my_list


def get_skill_mapping_data(skill_matrix_120, end):
	cond = get_conditions(skill_matrix_120)
	result = frappe.db.sql(""" select  sub_skill, sum(none_field), sum(beginner), sum(imtermediatory), sum(expert)  
								from `tabSkill Mapping Details` where parenttype = 'Skill Mapping' %s  
								 group by sub_skill """%(cond), as_list=1)
	result_list = [["Skill Matrix 120", "Naive", "Beginner", "Intermediatory", "Expert"]]
	result_list.extend([ list(row) for row in result ])
	return { "requests":  result_list }

def get_conditions(skill_matrix_120):
	cond = ""
	if skill_matrix_120:
		skill_matrix_18 = frappe.db.get_value("Skill Matrix 120", skill_matrix_120, "skill_matrix_18")
		cond = " and skill = '%s' "%skill_matrix_18
	return cond						   