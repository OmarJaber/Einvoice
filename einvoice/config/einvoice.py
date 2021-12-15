from __future__ import unicode_literals
from frappe import _


def get_data():
	return [
		{
			"label": _("E-Invoice"),
			"items": [
				{
					"type": "doctype",
					"label": "Item",
					"name": "EInvoice Item",
					"onboard": 1
				},
				{
					"type": "doctype",
					"label": "Item Group",
					"name": "EInvoice Item Group",
					"onboard": 1
				},
				{
					"type": "doctype",
					"name": "Taxes",
					"onboard": 1
				},
				{
					"type": "doctype",
					"label": "Sales Invoice",
					"name": "EInvoice Sales Invoice",
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
