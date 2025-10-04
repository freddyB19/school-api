QUERY_CREATE_USER = """
	mutation CreateUser($school_id: Int!, $user: UserInput!){
		createUser(schoolId: $school_id, user: $user){
			user {
				id
				name
				email
				role
			}
		}
	}
"""