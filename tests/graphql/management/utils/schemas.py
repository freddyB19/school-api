QUERY_ADMINISTRATOR_DETAIL = """
query MyQuery($pk: ID!, $limit: Int=3, $offset: Int=0) {
	administrator(pk: $pk) {
		... on Administrator {
			id
			school {
				id
				name
				subdomain
			}
			users(pagination: {limit: $limit, offset: $offset}) {
				totalCount
				results {
					dateJoined
					email
					id
					lastLogin
					name
				}
			}
		}
		... on AdminResponse {
			__typename
			messages {
				code {
					code
					status
				}
				kind
				message
			}
		}
  }
}
"""