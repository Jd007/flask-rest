class CommonThrottle(object):

	'''
	The base class for all throttles. Throttling is processed before each request reaches the REST endpoint.
	'''

	def __init__(self):
		# Simple, 1-letter codes for request methods, can be used to do HTTP request method based throttling
		self.THROTTLE_METHOD_TYPE_MAP = {'get': 'g',
										'head': 'g',
										'post': 'p',
										'put': 'u',
										'patch': 'a',
										'delete': 'd',
										'options': 'o'}

		# Simple codes for REST resources that need throttling, can be used to do resource based throttling
		self.THROTTLE_RESOURCE_MAP = {} # {<REST_resource_class_name>: <short_code>}

	def throttle(self, throttle_override=None):

		'''
		The throttle handling function. Returns a boolean of whether the request should be throttled or not.
		Override to provide the actual throttling functionality. Throttle on/off toggle can be forced by
		passing in the throttle_override parameter.
		'''

		return False

class StrictThrottle(CommonThrottle):

	'''
	An example throttle implementation. If throttling is turned on, all requests are throttled, else no requests
	are throttled.
	'''

	def __init__(self):
		CommonThrottle.__init__(self)

	def throttle(self, throttle_override=None):
		if throttle_override is not None:
			throttle_enabled = (throttle_override == 1)
		return not throttle_enabled

strict_throttle = StrictThrottle()