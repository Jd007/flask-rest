try: import simplejson as json
except ImportError: import json
from flask_rest import app
from flask_rest.utils.restview import RESTView
from flask_rest.utils.auth import NoopAuthorization, ExampleAuthorization
from flask_rest.utils.throttle import strict_throttle

class ExampleHandler(RESTView):

	def __init__(self):
		self.allowed_methods = ('GET', 'POST', 'PUT', 'DELETE') # 4 methods are allowed here

		self.auth_methods = {'ALL': ExampleAuthorization(), # All methods use ExampleAuthorization to authenticate...
							'GET': NoopAuthorization()} # ... Except for GET, which uses NoopAuthorization

		self.throttle_options = {'ALL': (strict_throttle, False), # All methods use strict_throttle for traffic control, with throttling override to off
								'GET': (strict_throttle, False)} # Can be customized per method (not done here)

		self.default_cut_size = 5 # Default range of resources to retrieve if range not specified (prevent retrieving too many objects)

	@classmethod
	def register_handler(clss, endpoint_name, url, resource_id_name, resource_id_type):
		view_func = clss.as_view(endpoint_name) # Register endpoint name

		# Plain URL with optional resource ID after it (i.e. "/url" or "/url/resource_id"); GET, PUT, DELETE, HEAD, and OPTIONS allowed
		app.add_url_rule(url, defaults={'example_resource_id': None}, view_func=view_func, methods=['GET', 'PUT', 'DELETE', 'HEAD', 'OPTIONS'])

		# Plain URL (i.e. "/url"); POST uses this
		app.add_url_rule(url, view_func=view_func, methods=['GET', 'POST', 'HEAD', 'OPTIONS'])

		# URL with int resource ID following it (i.e. "/url/4")
		app.add_url_rule('%s<%s:%s>' % (url, 'int', 'example_resource_id'), view_func=view_func, methods=['GET', 'PUT', 'DELETE', 'HEAD', 'OPTIONS'])

		# URL with range following it (i.e. "/url/1;3"), for retrieving a range of resources. Starts at 1
		app.add_url_rule('%s<%s:%s>;<%s:%s>' % (url, 'int', 'lower_cut', 'int', 'upper_cut'), view_func=view_func, methods=['GET', 'HEAD', 'OPTIONS'])

	def get(self, auth_data_obj, example_resource_id=None, lower_cut=None, upper_cut=None):
		if example_resource_id is not None:
			# Retrieve resource by known ID
			resource_data = {'example_obj_id': example_resource_id,
							'example_obj_data': 'API v2 example handler text data for ID ' + str(example_resource_id)}

			# Every method
			return ('ALL_OK', resource_data)
		else:
			# Ranged query on resource
			if lower_cut is None:
				# Use the default cut size
				lower_cut = 1
				upper_cut = self.default_cut_size
			lower_cut -= 1
			upper_cut -= 1
			if lower_cut >= upper_cut or lower_cut < 0:
				# Invalid ranged query, return error
				return ('BAD_REQUEST', None)
			return_data = []
			for i in range(lower_cut, upper_cut):
				resource_data = {'example_obj_id': i,
								'example_obj_data': 'API v2 example handler text data for ID ' + str(i)}
				return_data.append(resource_data)

			return ('ALL_OK', return_data)

	def post(self, auth_data_obj):
		# Creating a new resource. Not done here, but showing how authentication data can be used here
		return ('CREATED', auth_data_obj['user_name'])

	def put(self, auth_data_obj, example_resource_id=None):
		if example_resource_id is None:
			# For modification, resource ID must be provided.
			return ('BAD_REQUEST', None)

		# Data modification done here
		pass

		# Call get to retrieve the updated resource data
		return self.get(auth_data_obj, example_resource_id=example_resource_id, lower_cut=None, upper_cut=None)

	def delete(self, auth_data_obj, example_resource_id=None):
		if example_resource_id is None:
			# For deletion, resource ID must be provided.
			return ('BAD_REQUEST', None)

		# Process the deletion
		pass

		return ('DELETED', None)