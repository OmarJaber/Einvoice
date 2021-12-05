from __future__ import unicode_literals
from frappe import _


def get_data():
	return [
		{
			"label": _("E-Invoice"),
			"items": [
				{
					"type": "doctype",
					"name": "Item",
					"onboard": 1
				},
				{
					"type": "doctype",
					"name": "Item Group",
					"onboard": 1
				},
				{
					"type": "doctype",
					"name": "Taxes",
					"onboard": 1
				},
				{
					"type": "doctype",
					"name": "Sales Invoice",
					"onboard": 1
				}
			]
		},
		{
			"label": _("Settings"),
			"items": [
				{
					"type": "doctype",
					"name": "Company Info",
					"onboard": 1
				}
			]
		},
	]
