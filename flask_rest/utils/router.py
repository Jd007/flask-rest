from flask_rest import app

def register_handlers(api_ver):

	'''
	All REST endpoint handlers are registered for routing here. The actual sub-URL routing for each
	RESTful resource is specified within each resource's implementation. Here the register_handler
	method is called with the base resource name in the API.
	'''

	if api_ver == 'v1':
		# Register REST handlers for API version 1
		from flask_rest.example_api_v1.example_handler import *

		# Example handler v1
		ExampleHandler.register_handler('rest_example', '/%s/rest_example/' % (api_ver), None, None)

	elif api_ver == 'v1':
		# Register REST handlers for API version 1
		from flask_rest.example_api_v2.example_handler import *

		# Example handler v2
		ExampleHandler.register_handler('rest_example', '/%s/rest_example/' % (api_ver), None, None)