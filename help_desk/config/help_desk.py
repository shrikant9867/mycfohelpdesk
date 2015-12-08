from __future__ import unicode_literals
from frappe import _


def get_data(): 
	return [
		{
			"label": _("Documents"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Request",
					"description": _("List Of Requests"),
				},
			]
		},
		{
			"label": _("Masters"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Department Name",
					"description": _("List of Departments"),
				},
				{
					"type": "doctype",
					"name": "Request Category",
					"description": _("Request Category"),
				},
				{
					"type": "doctype",
					"name": "TAT",
					"description": _("Turn Around Time"),
				},
				{
					"type": "doctype",
					"name": "Sub Request Category",
					"description": _("Sub Request"),
				},
			]
		}
	]		