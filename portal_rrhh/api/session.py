import frappe


@frappe.whitelist()
def get_users():
	query = frappe.qb.get_query(
		"User",
		fields=["name", "email", "enabled", "user_image", "full_name", "user_type"],
		order_by="full_name asc",
		distinct=True,
	)

	roles = frappe.get_roles()
	if "System Manager" not in roles and "HR Manager" not in roles and "RRHH Manager" not in roles:
		query = query.where(frappe.qb.DocType("User").name == frappe.session.user)

	users = query.run(as_dict=1)

	for user in users:
		if frappe.session.user == user.name:
			user.session_user = True

		# Para RRHH, consideramos manager a los que tienen roles de RRHH Manager o Administrator
		user.is_manager = (
			"RRHH Manager" in frappe.get_roles(user.name) or
			"HR Manager" in frappe.get_roles(user.name) or
			user.name == "Administrator"
		)
	return users
