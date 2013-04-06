from flask_rest import app
from flask_rest.utils.http_utils import rf

# Overriding some common HTTP error codes, to return simpler RESTful responses.

@app.errorhandler(400)
def bad_request(e):
	return rf.get_response('BAD_REQUEST')

@app.errorhandler(404)
def not_found(e):
	return rf.get_response('NOT_FOUND')

@app.errorhandler(405)
def not_allowed(e):
	return rf.get_response('NOT_ALLOWED')

@app.errorhandler(413)
def request_entity_too_large(e):
	return rf.get_response('REQUEST_ENTITY_TOO_LARGE')

@app.errorhandler(500)
def internal_error(e):
	return rf.get_response('INTERNAL_ERROR')