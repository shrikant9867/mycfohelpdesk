frappe.provide('report.graphicalReports')

frappe.pages['graphical-reports'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Graphical Reports',
		single_column: false
	});
	new report.graphicalReports(wrapper, page)
}

report.graphicalReports = Class.extend({
	init: function(wrapper, page) {
		var me = this;
		
		this.make_sidebar(page);
		this.make_filters(wrapper);
		this.bind_filters();

		this.title_mapper = {
			"tat-closed-tickets": "TAT For Closed Tickets",
			"total-request-generated": "Total Request Generated"
		}

		this.report = $('<div class="graphical-report"></div>').appendTo(this.page.main);

		if(frappe.google_charts_loaded)
			me.refresh();
		else
			window.setTimeout(function(){
				me.refresh();
			}, 1000);
	},
	make_sidebar: function(page){
		var me = this;
		page.sidebar.html(frappe.render_template("report_sidebar", { data: this.get_list_of_reports()}));
		page.sidebar.on("click", ".module-sidebar-item", function(e){
			report = $(this).attr("report-name")
			subtitle = me.title_mapper[report]? " - " + me.title_mapper[report] : ""
			title = "Graphical Reports"+ subtitle
			$(".page-title > h1 > .title-text").html(title)
			me.refresh();
		})
	},
	get_list_of_reports: function(){
		return {
			data: [{
					"icon": "icon-star",
					"id": "tat-closed-tickets",
					"label": "TAT For Closed Tickets"
				},
				{
					"icon": "icon-star",
					"id": "total-request-generated",
					"label": "Total Request Generated"
			}]
		}
	},
	make_filters: function(wrapper){
		var me = this;
		this.page = wrapper.page;

		this.page.set_primary_action(__("Refresh"),
			function() { me.refresh(); }, "icon-refresh")

		this.start = this.page.add_field({fieldtype:"Date", label:"From Date", fieldname:"start", reqd:1,
			default:dateutil.add_days(dateutil.get_today(), -30)});
		this.end = this.page.add_field({fieldtype:"Date", label:"To Date", fieldname:"end", reqd:1,
			default:dateutil.get_today()});
	},
	bind_filters:function(){
		var me = this
		this.start.$input.change(function(){
			me.validate_fields_and_refresh();
		});
		this.end.$input.change(function(){
			me.validate_fields_and_refresh();
		});
	},
	validate_fields_and_refresh: function(me){
		if(this.check_mandatory_fields()){
			start = new Date(this.page.fields_dict.start.get_parsed_value());
			end = new Date(this.page.fields_dict.end.get_parsed_value());
				
			if(end < start){
				frappe.msgprint("To Date must be greater than From Date", "Validate Error");
			}
			else{
				this.refresh();
			}
		}
	},
	refresh: function(report_name){
		var me = this;
		
		if(!report_name)
			report_name = "tat-closed-tickets";

		if(!this.check_mandatory_fields())
			return

		return frappe.call({
			method: "help_desk.help_desk.page.graphical_reports.graphical_reports.get",
			type: "GET",
			args: {
				start: this.page.fields_dict.start.get_parsed_value(),
				end: this.page.fields_dict.end.get_parsed_value(),
				report: report_name,
			},
			callback: function(r){
				if(r.message && r.message.requests && r.message.requests.length > 0){
					$(".graphical-report").empty()
					$('<div id="report"></div><div id="table"></div>').appendTo(".graphical-report");
					me.requests = r.message.requests;
					me.draw_chart();
					me.report.find("#table").html(frappe.render_template("graphical_table", { "table": r.message.table}));
				}
				else{
					$(".graphical-report").empty()
					$('<div class="msg-box" style="width: 63%; margin: 30px auto;"> \
						<p class="text-center">Requests not found for the selected \
						filters</p></div>').appendTo(".graphical-report");
				}
			}
		});
	},
	check_mandatory_fields: function(){
		start = this.page.fields_dict.start.get_parsed_value()
		end = this.page.fields_dict.end.get_parsed_value()

		if(!(start || end)){
			frappe.msgprint("From Date and To Date are mandatory", "Validate Error");
			return false
		}
		else if(!start){
			frappe.msgprint("From Date is mandatory", "Validate Error");
			return false
		}
		else if(!end){
			frappe.msgprint("To Date is mandatory", "Validate Error");
			return false
		}
		else
			return true
	},
	draw_chart: function(){
		var me = this;
		if(!me.requests && me.requests.length == 0)
			return

		var data = google.visualization.arrayToDataTable(me.requests);
		var view = new google.visualization.DataView(data);

		var options_fullStacked = {
			isStacked: 'percent',
			height: 400,
			legend: {position: 'top', maxLines: 3},
			vAxis: {
				minValue: 0,
				ticks: [0, .2, .4, .6, .8, 1]
			}
		};
		var chart = new google.visualization.ColumnChart(me.report.find("#report")[0]);
		chart.draw(view, options_fullStacked);
	}
});