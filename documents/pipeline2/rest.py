import httplib
import logging

from lxml import etree
from urlparse import urlparse

logger = logging.getLogger(__name__)

def xml_from_string(xmlstr):
    return etree.fromstring(xmlstr) if xmlstr else None

def send_request(uri, request_handler, response_handler, method, data=None):
    parseduri = urlparse(uri)
    connection = httplib.HTTPConnection(parseduri.netloc)
    try:
        request_handler(connection, parseduri, data)
        response = connection.getresponse()
        logger.info("Response was %s", response.reason)
        return response_handler(response)
    except httplib.HTTPException:
        logger.exception("%s failed for %s", method, uri)
        raise

def get_resource(uri):
    """Return a string representation of a resource"""

    def request_handler(connection, uri, *args):
        connection.request("GET", uri.path + "?" + uri.query)

    def response_handler(response):
        if response.status == httplib.OK:
            return response.read()
        else:
            logger.warn("Unexpected Server Response %s", response.status)
            return None

    return send_request(uri, request_handler, response_handler, "GET")

def get_resource_as_xml(uri):
    """Return an XML document representing a resource"""
    resource = get_resource(uri)
    return xml_from_string(resource)

def post_resource(uri, data):
    """Post a new resource"""

    def request_handler(connection, uri, data):
        connection.request("POST", uri.path + "?" + uri.query, data)

    def response_handler(response):
        if response.status == httplib.CREATED:
            return xml_from_string(response.read())
        else:
            logger.warn("Unexpected Server Response %s", response.status)
            return None

    return send_request(uri, request_handler, response_handler, "POST", data=data)

def delete_resource(uri):
    """Delete a resource from the server"""

    def request_handler(connection, uri, *args):
        connection.request("DELETE", uri.path + "?" + uri.query)

    def response_handler(response):
        if response.status == httplib.NO_CONTENT:
            return True
        else:
            logger.warn("Unexpected Server Response %s", response.status)
            return None

    return send_request(uri, request_handler, response_handler, "DELETE")
