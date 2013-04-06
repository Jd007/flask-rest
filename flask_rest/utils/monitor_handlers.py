from flask_rest import app
from flask_rest.utils.http_utils import rf

@app.route('/ping')
def health_check_ping():

	'''
	Used by load balancers to do health checks, if applicable. This default implementation
	only checks for server reachability, but can be easily extended to check for more info
	such as database connectivity.
	'''

	return rf.get_response('ALL_OK', '')