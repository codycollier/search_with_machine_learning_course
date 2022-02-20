import os

from flask import g, current_app
from opensearchpy import OpenSearch

# Create an OpenSearch client instance and put it into Flask shared space for use by the application
def get_opensearch():
    if 'opensearch' not in g:

        # Implement a client connection to OpenSearch so that the rest of the application can communicate with OpenSearch
        # g.opensearch = None
        # reference: https://corise.com/course/search-with-machine-learning/week/contentweek_ckxe4tene00211gcj0qoc7bxj/module/module_ckybcq1g10062149ndsu1d0bo

        # config (requires: > export ES_CREDS="foo:baz")
        host = 'localhost'
        port = 9200
        creds = os.environ.get("ES_CREDS", "foo:baz")

        # initialize and set client
        client = OpenSearch(
            hosts = [{'host': host, 'port': port}],
            http_compress = True,
            http_auth = creds,
            use_ssl = True,
            verify_certs = False,
            ssl_assert_hostname = False,
            ssl_show_warn = False,
        )
        g.opensearch = client

    return g.opensearch
