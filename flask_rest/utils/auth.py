from flask import request
from flask_rest.utils.http_utils import rf

class CommonAuthorization(object):

	'''
	Base authorization class, with get_challenge method implemented to return an
	HTTP Unauthorized (401) response with the required authentication method.
	'''

	def __init__(self):
		self.name = 'CommonAuth' # Name of the authorization method, used to hint the client on auth failure

	def is_authenticated(self):

		'''
		The core of the authorization class, and auth processing should be added here.
		Returns a 2-tuple, (<auth_status>, <auth_data_obj>), where <auth_status> is a
		boolean denoting whether the authorization was successful, and <auth_data_obj>
		is a dict containing any information on the authorization (e.g. user data),
		which can be passed along to the REST endpoint to reduce amount of DB reads (if
		applicable).
		'''

		return (False, {})

	def get_challenge(self, data=None):

		'''
		On failed authentication, this method returns the appropriate HTTP response to
		the client. Default is the standard Unauthorized response with the authorization
		method's name in the "WWW-Authenticate" header.
		'''

		return rf.get_response('UNAUTHORIZED', data=data, headers={'WWW-Authenticate': self.name})

class NoopAuthorization(CommonAuthorization):

	'''
	A no-op authorization class. All requests are allowed through. Used for debugging.
	'''

	def __init__(self):
		self.name = 'Noop'

	def is_authenticated(self):
		return (True, {})

class ExampleAuthorization(CommonAuthorization):

	'''
	An example authorization class, only requests with the correct access key are allowed through.
	Access keys and associated client information are stored in the class for this example. In
	a real implementaion they will most likely come from DBs.

	Takes an HTTP Authorization string in the format of:

		"ExampleAuth <access_key>"

	The <auth_data_obj> returned contains data on the user that the access key belongs to.
	'''

	def __init__(self):
		self.name = 'ExampleAuth'
		self.__allowed_users = {'not-so-random-access-key-qwerty': {'user_name': 'John',
																	'email': 'john@example.com'},
								'not-so-random-access-key-123456': {'user_name': 'Jane',
																	'email': 'jane@example.com'}}

	def is_authenticated(self):
		incoming_auth_str = request.headers.get('Authorization', None)
		if (not incoming_auth_str):
			return (False {})
		auth_str_split = incoming_auth_str.split(' ', 1)
		if len(auth_str_split) != 2:
			return (False, {})
		auth_method, incoming_access_key = auth_str_split
		if auth_method.lower() != self.name.lower() or incoming_access_key not in self.__allowed_users:
			return (False, {})
		return (True, self.__allowed_users[incoming_access_key])