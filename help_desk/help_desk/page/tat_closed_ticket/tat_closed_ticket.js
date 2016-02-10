
frappe.provide('report.totalRequestGenerated')

frappe.pages['tat-closed-ticket'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'TAT for Closed Ticket',
		single_column: true
	});

	new report.tatForClosedTicket(wrapper, page)
}

report.tatForClosedTicket = Class.extend({
	init: function(wrapper, page) {
		this.make_filters(wrapper)
		this.bind_filters()
		
		var me = this;
		this.report = $('<div class="graphical-report"></div>').appendTo(this.page.main);

		$.getScript("https://www.gstatic.com/charts/loader.js", function(){
			google.charts.load("current", {packages:['corechart']});
			google.charts.setOnLoadCallback(me.draw_chart);
		});

		this.refresh();
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
	refresh: function(){
		if(!this.check_mandatory_fields())
			return

		var me = this;

		return frappe.call({
			method: "help_desk.help_desk.page.tat_closed_ticket.tat_closed_ticket.get_tat_for_closed_ticket",
			type: "GET",
			args: {
				start: this.page.fields_dict.start.get_parsed_value(),
				end: this.page.fields_dict.end.get_parsed_value(),
			},
			callback: function(r){
				if(r.message.requests && r.message.requests.length > 0){
					me.requests = r.message.requests;
					me.draw_chart();
				}
				else
					frappe.msgprint("Requests not found for the selected filters")

				delete r.message["requests"]
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
	render_stacked_column_chart: function(){
		var me = this;

		if(!me.requests)
			return

		$.getScript("https://www.gstatic.com/charts/loader.js", function(){
			google.charts.load("current", {packages:['corechart']});
			google.charts.setOnLoadCallback(function(){
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
				var chart = new google.visualization.ColumnChart($(".graphical-report")[0]);
				chart.draw(view, options_fullStacked);
			});
		});
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
		var chart = new google.visualization.ColumnChart($(".graphical-report")[0]);
		chart.draw(view, options_fullStacked);
	}
});