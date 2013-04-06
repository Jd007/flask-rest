try: import simplejson as json
except ImportError: import json
from flask_rest import app
from flask_rest.utils.restview import RESTView
from flask_rest.utils.auth import NoopAuthorization
from flask_rest.utils.throttle import strict_throttle

'''
See example_handler in example_api_v2 for detailed info. Simple stub resource implemented
here in v1 to show how API version can be used to provide different API versions.
'''

class ExampleHandler(RESTView):

	def __init__(self):
		self.allowed_methods = ('GET',) # Only GET is allowed
		self.auth_methods = {'ALL': NoopAuthorization()}
		self.throttle_options = {'ALL': (strict_throttle, False)}

	@classmethod
	def register_handler(clss, endpoint_name, url, resource_id_name, resource_id_type):
		view_func = clss.as_view(endpoint_name)
		app.add_url_rule(url, view_func=view_func, methods=['GET', 'HEAD', 'OPTIONS'])

	def get(self, auth_data_obj):
		return_data = {'example_obj_id': 1,
						'example_obj_data': 'API v1 example handler text data'}
		return ('ALL_OK', return_data)