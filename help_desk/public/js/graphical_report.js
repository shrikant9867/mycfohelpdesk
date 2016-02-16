frappe.provide('report')

report.graphicalReports = Class.extend({
	init: function(wrapper, page, opts) {
		var me = this;

		this.rpt_name = opts["default_rpt"];
		this.title_mapper = opts["title_mapper"];
		this.stacked_percent_chart = opts["stacked_percent_chart"] || [];
		this.stacked_chart = opts["stacked_chart"] || [];
		this.line_chart = opts["line_chart"] || [];
		this.sidebar_items = opts["sidebar_items"];
		
		this.make_sidebar(page);
		this.make_filters(wrapper);
		this.bind_filters();

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
		page.sidebar.html(frappe.render_template("report_sidebar", { data: this.sidebar_items}));
		page.sidebar.on("click", ".module-sidebar-item", function(e){
			$(".module-sidebar-item").removeClass("active");
			$(this).addClass("active");

			me.rpt_name = $(this).attr("report-name")
			subtitle = me.title_mapper[me.rpt_name]? " - " + me.title_mapper[me.rpt_name] : ""
			title = "Graphical Reports"+ subtitle

			$(".page-title > h1 > .title-text").html(title)
			me.refresh();
		})
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
		this.toggle_filters()
	},
	toggle_filters: function(val){
		// this.start.$wrapper.readonlyDatepicker(true)
		// console.log(this.start.$wrapper);
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
		var me = this;
		
		if(!this.check_mandatory_fields())
			return

		return frappe.call({
			method: "help_desk.reports.get",
			type: "GET",
			args: {
				start: this.page.fields_dict.start.get_parsed_value(),
				end: this.page.fields_dict.end.get_parsed_value(),
				report: me.rpt_name,
			},
			callback: function(r){
				if(r.message && r.message.requests && r.message.requests.length > 0){
					$(".graphical-report").empty()
					$('<div id="report"></div><div id="table"></div>').appendTo(".graphical-report");
					me.requests = r.message.requests;
					me.draw_chart();
					if(r.message.table)
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
		var chart = new google.visualization.ColumnChart(me.report.find("#report")[0]);

		if(in_list(me.line_chart, me.title_mapper[me.rpt_name])){
			var chart = new google.visualization.LineChart(me.report.find("#report")[0]);
			chart.draw(data, option);
			$("<br>").appendTo(me.report.find("#report"))
		}
		else{
			var view = new google.visualization.DataView(data);
			var option = this.get_chart_options()
			chart.draw(view, option);
		}
	},
	get_chart_options: function(type, is_stacked){
		var me = this;

		if(in_list(this.stacked_percent_chart, me.title_mapper[me.rpt_name])){
			return {
					isStacked: 'percent',
					height: 400,
					legend: {position: 'top', maxLines: 3},
					vAxis: {
						minValue: 0,
						ticks: [0, .2, .4, .6, .8, 1]
					}
				};
		}
		else if(in_list(this.stacked_chart, me.title_mapper[me.rpt_name])){
			return {
					isStacked: 'percent',
					height: 400,
					legend: {position: 'top', maxLines: 3},
					vAxis: {
						minValue: 0,
						ticks: [0, .2, .4, .6, .8, 1]
					}
				};
		}
		else if(in_list(this.line_chart, me.title_mapper[me.rpt_name])){
			return {
				title: me.title_mapper[me.rpt_name] || "",
				curveType: 'function',
				legend: { position: 'bottom' }
			};
		}
	}
});
