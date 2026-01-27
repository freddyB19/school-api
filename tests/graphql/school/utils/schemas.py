QUERY_SCHOOL = """
query MyQuery($subdomain: String!) {
	coordinate(first: 10, filters: {school: {subdomain: $subdomain}}) {
	  edges {
	    node {
	      latitude
	      longitude
	      title
	    }
	  }
	  totalCount
	  pageInfo {
	    hasNextPage
	    hasPreviousPage
	  }
	}
	news(first: 10, filters: {school: {subdomain: $subdomain}}) {
	  totalCount
	  edges {
	    node {
	      id
	      media {
	      	photo
	      }
	      title
	      updated
	      created
	    }
	  }
	  pageInfo {
	    hasNextPage
	    hasPreviousPage
	  }
	}

	socialmedia(filters: {school: {subdomain: $subdomain}}) {
	  profile
	}
	settings(filters: {school: {subdomain: $subdomain}}) {
	  colors {
	    color
	  }
	}
	school(subdomain: $subdomain) {
	  address
	  id
	  logo
	  name
	  private
	  subdomain
	}

	download(filters: {school: {subdomain: $subdomain}}, first: 10) {
	  edges {
	    node {
	      file
	      id
	      title
	    }
	  }
	  pageInfo {
	    hasNextPage
	    hasPreviousPage
	  }
	}

	repository(
	  filters: {school: {subdomain: $subdomain}}
	  first: 10
	  ordering: {created: DESC}
	) {
	  edges {
	    node {
	      created
	      id
	      media {
	        file
	        title
	      }
	      nameProject
	      updated
	    }
	  }
	  pageInfo {
	    hasNextPage
	    hasPreviousPage
	  }
	}

	infraestructure(
	  filters: {school: {subdomain: $subdomain}}
	  first: 10
	  ordering: {name: ASC}
	) {
	  edges {
	    node {
	      id
	      media {
	        photo
	      }
	      name
	    }
	  }
	  pageInfo {
	    hasNextPage
	    hasPreviousPage
	  }
	} 
}
"""

QUERY_SCHOOL_CALENDAR = """
query MyQuery($subdomain: String!, $month: MonthsEnum) {
  calendar(
    month: $month,
    subdomain: $subdomain,
    order: {date: ASC},
    pagination: {limit: 10}
  ) {
    results {
      id
      title
      date
    }
    totalCount
    pageInfo {
      limit
      offset
    }
  }
}
"""

__all__ = [
	"QUERY_SCHOOL",
	"QUERY_SCHOOL_CALENDAR"
]