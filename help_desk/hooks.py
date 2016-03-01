# -*- coding: utf-8 -*-
from __future__ import unicode_literals

app_name = "help_desk"
app_title = "Help Desk"
app_publisher = "Indictrans"
app_description = "App For Managing issues related to employees"
app_icon = "icon-th"
app_color = "green"
app_email = "jitendra.k@indictranstech.com"
app_version = "0.0.1"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/help_desk/css/help_desk.css"
app_include_js = "/assets/js/help_desk.min.js"

# include js, css files in header of web template
# web_include_css = "/assets/help_desk/css/help_desk.css"
# web_include_js = "/assets/help_desk/js/help_desk.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "help_desk.install.before_install"
# after_install = "help_desk.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "help_desk.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

permission_query_conditions = {
	"Request":"help_desk.help_desk.doctype.request.request.get_permission_query_conditions",
}
#
# has_permission = {
# 	"Event": "help_desk.help_desk.doctype.request.request.get_permission_query_conditions",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"daily": [
# 		"help_desk.tasks.daily"
# 	],
# }

# Testing
# -------

# before_tests = "help_desk.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "help_desk.event.get_events"
# }

