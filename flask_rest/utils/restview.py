import time, datetime
from flask import request
from flask.views import View
from flask_rest import app
from flask_rest.utils.http_utils import rf, ipv4_str_to_int, get_request_data_dict
from flask_rest.utils.auth import NoopAuthorization
from flask_rest.utils.throttle import strict_throttle

class RESTView(View):

	'''
	Custom view for RESTful classes (similar to Flask's built-in MethodView, but more flexible).

	Base class for all REST resource endpoint handlers.
	'''

	def __init__(self):
		self.allowed_methods = () # List of allowed HTTP methods on the resource, in upper case (e.g. "GET")
		self.auth_methods = {'ALL': NoopAuthorization()} # Authorizatin can be customized per request method
		# Default throttling options; throttle handler object and whether to override throttle On/Off (None means use default) can be set per method
		self.throttle_options = {'ALL': (strict_throttle, False)} # {<method_name>: (<throttle_obj>, <throttle_enabled_override>)}

	@classmethod
	def register_handler(clss, endpoint_name, url, resource_id_name, resource_id_type):

		'''
		Default URL routing configuration, called by the API's router to register the resource to the API.
		Override to provide resource-specific URL routing schemes.

		Parameters passed in:
			endpoint_name: name of the API endpoint, str
			url: the relative URL path to the resource, str
			resource_id_name: the name of the ID for this REST resource, str
			resource_id_type: the resource ID data type (e.g. int, str...)

		By default, a reasonable set of routing schemes are supported for the appropriate HTTP methods.
		Ranged queries on GET are also supported by default, through "/url/1;5" format.
		'''

		view_func = clss.as_view(endpoint_name)
		app.add_url_rule(url, defaults={resource_id_name: None}, view_func=view_func, methods=['GET', 'HEAD', 'OPTIONS'])
		app.add_url_rule('%s<%s:%s>;<%s:%s>' % (url, 'int', 'lower_cut', 'int', 'upper_cut'), view_func=view_func, methods=['GET', 'HEAD', 'OPTIONS'])
		app.add_url_rule(url, view_func=view_func, methods=['GET', 'POST', 'HEAD', 'OPTIONS'])
		app.add_url_rule('%s<%s:%s>' % (url, resource_id_type, resource_id_name), view_func=view_func, methods=['GET', 'PUT', 'DELETE', 'HEAD', 'OPTIONS'])

	def head(self, *args, **kwargs):

		'''
		Default handler for HTTP HEAD requests. Calls GET if exists, then returns the status
		code without response body.
		'''

		if 'GET' in self.allowed_methods:
			# Call get, then strip the body
			if getattr(self, 'get', None):
				response_name = self.get(*args, **kwargs)[0]
				return (response_name, None)
			else:
				return ('NOT_IMPLEMENTED', None)
		else:
			headers = {'Allow': sorted(request.url_rule.methods)}
			return ('NOT_ALLOWED', None, headers)

	def options(self, *args, **kwargs):

		'''
		Default handler for HTTP OPTIONS requests. Returns a list of allowed methods in the header.
		'''

		headers = {'Allow': sorted(request.url_rule.methods)}
		return ('ALL_OK', None, headers)

	def __log_request(self, processing_start, request_info, response_name):

		'''
		All incoming requests that come in can be logged, and is processed here.
		'''

		logging_data = get_request_data_dict() # Get some data associated with the current request for logging
		processing_time = time.time() - processing_start

		# By default nothing is logged, but can be easily added here (depending how logging is done).
		pass

	def dispatch_request(self, *args, **kwargs):

		'''
		Main request handler method.
		'''

		try:
			processing_start = time.time() # Keep track of time used per request, can be logged for monitoring
			extra_request_info = {} # A dict used to keep track of information gathered on the request that are not part of the request obj itself (e.g. client info)

			# Handler method check:
			request_method = request.method.upper()
			if request_method not in (self.allowed_methods + ('OPTIONS', 'HEAD')):
				# HTTP method not allowed on this REST resource, log the request, then return the appropriate response with a list of allowed methods
				self.__log_request(processing_start, extra_request_info, 'NOT_ALLOWED')
				headers = {'Allow': sorted(request.url_rule.methods)}
				return rf.get_response('NOT_ALLOWED', None, headers)

			# Get the HTTP method handler function
			handler_method = getattr(self, request_method.lower(), None)
			if handler_method is None:
				# The HTTP method handler function has not yet been created, but the method is allowed for the resource
				self.__log_request(processing_start, extra_request_info, 'NOT_IMPLEMENTED')
				return rf.get_response('NOT_IMPLEMENTED')

			# Handle authentication:
			authenticator = self.auth_methods.get(request_method, self.auth_methods['ALL'])
			is_authorized, auth_data_obj = authenticator.is_authenticated()
			extra_request_info['auth_data_obj'] = auth_data_obj # Attach the data obj returned by the authenticator for potential use and logging
			if not is_authorized:
				# Access denied, log the request and return the corresponding auth challenge response
				self.__log_request(processing_start, extra_request_info, 'UNAUTHORIZED')
				return authenticator.get_challenge()

			# Handle request throttling:
			method_throttle_options = self.throttle_options.get(request_method, self.throttle_options['ALL'])
			throttler, throttle_override = method_throttle_options
			is_throttled = throttler.throttle(self.__class__.__name__, throttle_override)
			if is_throttled:
				self.__log_request(processing_start, extra_request_info, 'THROTTLED')
				return rf.get_response('THROTTLED')

			# Response processing by the HTTP method handler function (actual API called here):
			try:
				handler_return = handler_method(auth_data_obj, *args, **kwargs)
			except:
				# Something went wrong with the handler's processing of the request. Log the error (possibly more detailed logging and
				# notification can be added here) and return an error response.
				self.__log_request(processing_start, extra_request_info, 'INTERNAL_ERROR')
				return rf.get_response('INTERNAL_ERROR')

			# Get API handler return data
			response_name, response_data = handler_return[:2]

			if response_name == 'UNAUTHORIZED' and response_data is None:
				# The more advanced auth system in the handler denied access, log it, then propagate this to the client
				self.__log_request(processing_start, extra_request_info, 'UNAUTHORIZED')
				return authenticator.get_challenge()

			response_headers = {}
			# Check if the API handler pass along any custom headers to add to the response
			if len(handler_return) == 3:
				response_headers = handler_return[2]
			response = rf.get_response(response_name, response_data, response_headers)

			# Log this request (response_data can be added to extra_request_info if response data should be logged)
			self.__log_request(processing_start, extra_request_info, response_name)
			if app.debug:
				# In debug mode, return the request processing time as a special header for reference
				response.headers['Processing-Time'] = time.time() - processing_start
			return response
		except:
			# Something went wrong with the RestView itself (very bad). Notification of the error can be added here.
			return rf.get_response('INTERNAL_ERROR')