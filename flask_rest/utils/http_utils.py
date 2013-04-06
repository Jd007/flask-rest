try: import simplejson as json
except ImportError: import json
import socket, struct
from flask import request, Response
from flask_rest.utils.data_utils import FlexibleJSONEncoder

class ResponseFactory(object):

	'''
	Generates a HTTP response object based on the name of the response type requested.
	The default implementation will serialize the response body data to JSON if
	needed/possible. Other serialization can be added.
	'''

	def __init__(self):
		# HTTP response codes
		self.HTTP_RESPONSE_CODES = {'ALL_OK': (200, 'OK'), # {<response_name>: (<response_code>, <response_txt_data>)}
									'CREATED': (201, 'Created'),
									'ACCEPTED': (202, 'Accepted'),
									'DELETED': (204, ''), # Do not send body
									'BAD_REQUEST': (400, 'Bad Request'),
									'UNAUTHORIZED': (401, 'Unauthorized'),
									'FORBIDDEN': (403, 'Forbidden'),
									'NOT_FOUND': (404, 'Not Found'),
									'NOT_ALLOWED': (405, 'Method Not Allowed'),
									'NOT_ACCEPTABLE': (406, 'Not Acceptable'),
									'CONFLICT': (409, 'Conflict'),
									'GONE': (410, 'Gone'),
									'REQUEST_ENTITY_TOO_LARGE': (413, 'Request Entity Too Large'),
									'INTERNAL_ERROR': (500, 'Internal Server Error'),
									'NOT_IMPLEMENTED': (501, 'Not Implemented'),
									'THROTTLED': (503, 'Service Unavailable')}

		# Content type strs used
		self.RESPONSE_CONTENT_TYPES = {'json': 'application/json; charset=utf-8',
									'plaintext': 'text/plain; charset=utf-8'}

	def get_response(self, response_name, data=None, headers={}):

		'''
		Generates a response object that can be returned to the client, based on the response name.
		Data that can be serialized are automatically serialized using JSON by default. Other serializers
		can be added to flask_rest.utils.data_utils and imported here to provide more response formats.

		Custom headers passed in are also set to the response.
		'''

		status, status_name = self.HTTP_RESPONSE_CODES.get(response_name, (500, 'Internal Server Error'))
		if data is None:
			data = status_name
			content_type = self.RESPONSE_CONTENT_TYPES.get('plaintext')
		elif isinstance(data, str):
			content_type = self.RESPONSE_CONTENT_TYPES.get('plaintext')
		else:
			content_type = self.RESPONSE_CONTENT_TYPES.get('json')

		# Serialized list, dict, and tuple data types
		if isinstance(data, (list, dict, tuple)):
			data = json.dumps(data, cls=FlexibleJSONEncoder)
		response = Response(response=data, status=status, headers=headers, mimetype=content_type, content_type=content_type, direct_passthrough=False)
		return response

	def get_response_code(self, response_name):

		'''
		Returns the response code that matches the response name; returns -1 if the response name
		cannot be found.
		'''

		return self.HTTP_RESPONSE_CODES.get(response_name, (-1, ''))[0]

rf = ResponseFactory()

def ipv4_str_to_int(ipv4_str):
	# Returns the integer representation of a dotted IPv4 string (e.g. "184.169.43.8")
	return struct.unpack('!L', socket.inet_aton(ipv4_str))[0]

def ipv4_int_to_str(ipv4_int):
	# Returns the dotted string representation of the integer representation of an IPv4 address
	return socket.inet_ntoa(struct.pack('!L', ipv4_int))

def get_request_data_dict():
	# Returns a dictionary of parsed request data (for logging purposes). Can be customized here
	d = {'request_url': request.base_url,
		'request_method': {'GET': 0, 'POST': 1, 'PUT': 2, 'PATCH': 3, 'DELETE': 4, 'HEAD': 5, 'OPTIONS': 6}.get(request.method.upper(), -1),
		'extra_arg': request.path,
		'remote_address': request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip(),
		'request_data': json.dumps(request.json) if (len(request.data) > 0 and request.json is not None) else '',
		'request_query_str_data': json.dumps(request.args.to_dict(flat=False)),
		}
	return d