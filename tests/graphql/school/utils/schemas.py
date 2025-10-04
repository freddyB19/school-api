QUERY_SCHOOL_BY_SUBDOMAIN = """
query School($subdomain: String!) {
	schoolBySubdomain(subdomain: $subdomain) {
		school {
			id
			name
			subdomain
		}
		
		settings {
			color
		}

		networks {
			profile
		}
		
		news {
			id
			title
			photo
		}

		coordinates {
			id
			title
			latitude
			longitude
		}

	}
}
"""


QUERY_SCHOOL_SERVICE = """
query SchoolService($schoolId: Int!){
	schoolServiceOnline(schoolId: $schoolId) {
		downloads {
			id
			title
		}
		
		repositories {
			id
			project
		}
	}

	schoolServiceOffline(schoolId: $schoolId) {
		infraestructures {
			id
			photo
		}
	}
}

"""


QUERY_SCHOOL_CALENDAR = """
query SchoolCalendar($subdomain: String!, $month: Months, $first: Int) {
	schoolCalendar(subdomain: $subdomain, month: $month, first: $first) {
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
				title
				date
				calendarId
	        }
        }

	}
}
"""
