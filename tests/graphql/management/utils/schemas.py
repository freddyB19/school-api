QUERY_ADMINISTRATOR_DETAIL = """
	query AdministratorDetail($pk: Int!, $first: Int){

		detail(pk: $pk){
			id
			school {
				id
				name
			}
		}

		admins(pk: $pk, first: $first){
			pageInfo {
		        startCursor
		        endCursor
		        hasNextPage
		        hasPreviousPage
		    }
		    edges {
		        cursor
		        node {
					name
					email
					role
					userId
					dateJoined
					lastLogin
		        }
	        }
		}
	}
"""

QUERY_ADMINISTRATOR_DETAIL_ADMINS = """
	query AdministratorDetail($pk: Int!, $first: Int, $after: String){

		admins(pk: $pk, first: $first, after: $after){
			pageInfo {
		        startCursor
		        endCursor
		        hasNextPage
		        hasPreviousPage
		    }
		    edges {
		        cursor
		        node {
		            id
					name
					email
		        }
	        }
		}
	}
"""