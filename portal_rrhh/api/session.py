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

	# Optimization: Batch fetch roles to avoid N+1 queries
	if users:
		user_names = [u.name for u in users]
		
		# Find which users have manager roles
		managers = frappe.get_all(
			"Has Role",
			filters={
				"parent": ["in", user_names],
				"role": ["in", ["RRHH Manager", "HR Manager"]]
			},
			fields=["parent"],
			pluck="parent"
		)
		manager_set = set(managers)
		manager_set.add("Administrator")

		for user in users:
			if frappe.session.user == user.name:
				user.session_user = True

			user.is_manager = user.name in manager_set

	return users
