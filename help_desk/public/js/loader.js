frappe.google_charts_loaded = false;

$.getScript("https://www.gstatic.com/charts/loader.js", function(){
	google.charts.load("current", {packages:['corechart', 'bar']});
	google.charts.setOnLoadCallback(function(){
		frappe.google_charts_loaded = true;
	});
});
