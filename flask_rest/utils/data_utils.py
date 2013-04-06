try: import simplejson as json
except ImportError: import json
import time, datetime

class FlexibleJSONEncoder(json.JSONEncoder):

	'''
	A more powerful JSONEncoder that automatically serializes certain objects
	that the default encoder does not (e.g. datetime objects).
	'''

	def default(self, obj):
		if isinstance(obj, datetime.datetime):
			# Serialize datetime objects to Epoch time stamps
			# Timezone is assumed to be UTC
			return int(time.mktime(obj.timetuple()))
		return json.JSONEncoder.default(self, obj)

# Other data serializers can be added here to provide more return data formats for the API