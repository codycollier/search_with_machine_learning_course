#
# The main search hooks for the Search Flask application.
#
from flask import (
    Blueprint, redirect, render_template, request, url_for
)

from week1.opensearch import get_opensearch

bp = Blueprint('search', __name__, url_prefix='/search')


# Process the filters requested by the user and return a tuple that is appropriate for use in: the query, URLs displaying the filter and the display of the applied filters
# filters -- convert the URL GET structure into an OpenSearch filter query
# display_filters -- return an array of filters that are applied that is appropriate for display
# applied_filters -- return a String that is appropriate for inclusion in a URL as part of a query string.  This is basically the same as the input query string
def process_filters(filters_input):
    print("[debug] filters_input: {}".format(filters_input))

    # Filters look like: 
    #  range: &filter.name=regularPrice &regularPrice.key={{ agg.key }} &regularPrice.from={{ agg.from }} &regularPrice.to={{ agg.to }}
    #  range: &filter.name=regularPrice &regularPrice.type=range &regularPrice.key=20.0-* &regularPrice.from=20.0 &regularPrice.to= &regularPrice.displayName=Price
    #  terms: &filter.name=department &department.type=terms &department.key=MOBILE%20AUDIO &department.displayName=Department

    filters = []
    display_filters = []  # Also create the text we will use to display the filters that are applied
    applied_filters = ""
    for filter_name in filters_input:

        filter_type = request.args.get(f"{filter_name}.type")
        display_name = request.args.get(f"{filter_name}.displayName", filter_name)
        
        # We need to capture and return what filters are already applied so they can be automatically added to any existing links we display in aggregations.jinja2
        applied_filters += f"&filter.name={filter_name}&{filter_name}.type={filter_type}&{filter_name}.displayName={display_name}"

        # TODO(wip): implement and set filters, display_filters and applied_filters.
        # filters get used in create_query below
        # display_filters gets used by display_filters.jinja2
        # and applied_filters gets used by aggregations.jinja2 (and any other links that would execute a search.)

        if filter_type == "range":

            # Example:
            #  filter.name=regularPrice
            #  regularPrice.type=range
            #  regularPrice.key=20.0-*
            #  regularPrice.from=20.0
            #  regularPrice.to=
            #  regularPrice.displayName=Price
            #
            # {"range": {"regularPrice": {"gte": 100.0, "lte": 500}}}

            field = filter_name
            gte_val = request.args.get(f"{filter_name}.from", 0)
            lte_val = request.args.get(f"{filter_name}.to", '')
            if lte_val == "": lte_val = 123456789
            filters.append({"range": {field: {"gte": float(gte_val), "lte": float(lte_val)}}})

            display_filters.append(display_name)

        elif filter_type == "terms":

            # Example:
            #  filter.name=department
            #  department.type=terms
            #  department.key=MOBILE%20AUDIO
            #  department.displayName=Department
            #
            #  {"term": {"department": "AUDIO"}},

            field = filter_name
            value = request.args.get(f"{filter_name}.key")
            filters.append({"term": {field: value}})

            display_filters.append(display_name)


    print("[debug] Filters: {}".format(filters))
    return filters, display_filters, applied_filters


# Our main query route.  Accepts POST (via the Search box) and GETs via the clicks on aggregations/facets
@bp.route('/query', methods=['GET', 'POST'])
def query():

    # Load up our OpenSearch client from the opensearch.py file.
    opensearch = get_opensearch()

    # Put in your code to query opensearch.  Set error as appropriate.
    error = None
    user_query = None
    query_obj = None
    display_filters = None
    applied_filters = ""
    filters = None
    sort = "_score"
    sortDir = "desc"

    # a query has been submitted
    if request.method == 'POST':
        user_query = request.form['query']
        if not user_query:
            user_query = "*"
        sort = request.form["sort"]
        if not sort:
            sort = "_score"
        sortDir = request.form["sortDir"]
        if not sortDir:
            sortDir = "desc"
        query_obj = create_query(user_query, [], sort, sortDir)

    # Handle the case where there is no query or just loading the page
    elif request.method == 'GET':
        user_query = request.args.get("query", "*")
        filters_input = request.args.getlist("filter.name")
        sort = request.args.get("sort", sort)
        sortDir = request.args.get("sortDir", sortDir)
        if filters_input:
            (filters, display_filters, applied_filters) = process_filters(filters_input)

        query_obj = create_query(user_query, filters, sort, sortDir)
    else:
        query_obj = create_query("*", [], sort, sortDir)

    # TODO(done): Replace me with an appropriate call to OpenSearch
    # Postprocess results here if you so desire
    print("[debug] query obj: {}".format(query_obj))
    response = opensearch.search(body=query_obj, index="bbuy_products")

    if error is None:
        return render_template("search_results.jinja2", query=user_query, search_response=response,
                               display_filters=display_filters, applied_filters=applied_filters,
                               sort=sort, sortDir=sortDir)
    else:
        redirect(url_for("index"))


def create_query(user_query, filters, sort="_score", sortDir="desc"):
    print("[debug] Query: {} Filters: {} Sort: {}".format(user_query, filters, sort))

    query_obj = {
        'size': 10,
    }

    # TODO(done): aggregations
    query_obj["aggs"] = {
            "regularPrice": { "range": { "field": "regularPrice", "ranges": [{"from": 0, "to": 5}, {"from": 5, "to": 20}, {"from": 20}] }},
            "department": { "terms": {"field": "department", "size": 10 }},
            "missing_images": { "missing": {"field": "image"}}
            }

    # TODO(wip): query and filters
    # "query": {"bool": {
    #    "must": [ {"multi_match": {"query": "bass", "fields": ["name", "longDescription", "shortDescription"] } } ],
    #    "filter": [ {"term": {"department": "AUDIO"}} ]
    #    }}
    if user_query in (None, "*"):
        query_obj["query"] = {"bool": {
            "must": [ {"match_all": {}} ],
            "filter": filters
            }}
    elif user_query:
        query_obj["query"] = {"bool": {
            "must": [ {"multi_match": {"query": user_query, "fields": ["name", "longDescription", "shortDescription"] } } ],
            "filter": filters
            }}



    return query_obj





