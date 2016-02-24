frappe.require("assets/help_desk/js/graphical_report.js");

frappe.pages['helpdesk-reports'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Graphical Reports',
		single_column: false
	});

	opts = {
		title_mapper: {
			"tat-closed-tickets": "TAT For Closed Tickets",
			"total-request-generated": "Total Request Generated",
		},
		stacked_percent_chart: ["TAT For Closed Tickets", "Total Request Generated"],
		default_rpt: "tat-closed-tickets",
		sidebar_items: {
			data: [
				{
					"icon": "icon-star",
					"id": "tat-closed-tickets",
					"label": "TAT For Closed Tickets"
				},
				{
					"icon": "icon-star",
					"id": "total-request-generated",
					"label": "Total Request Generated"
				}
			]
		}
	}

	new report.graphicalReports(wrapper, page, opts)
}