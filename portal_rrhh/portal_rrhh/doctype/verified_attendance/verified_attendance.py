# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class VerifiedAttendance(Document):
	def validate(self):
		if self.verified_in_time and self.verified_out_time:
			if self.verified_out_time < self.verified_in_time:
				frappe.throw("Verified Out Time cannot be before Verified In Time")
