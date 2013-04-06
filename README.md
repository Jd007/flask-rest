### Flask REST API Template

A class-based template for building RESTful APIs in Flask. Provided here more as a reference for people who want to implement their own RESTful API, as opposed to a ready-to-go REST API framework.

##### Why:

* Many existing RESTful APIs did not offer the level of flexibility I wanted (e.g. request authentication are resource-wide and cannot be customized based on request method)
* Keep the overhead as little as possible (e.g. no useless serializers)

##### Requirements:

* Python 2.6.x or later
* Flask 0.8 or later

##### Features:

* Resource handlers return python data types (e.g. dict, list) instead of HTTP response, so they can be easily called from outside the REST context to get the raw response data
* Request authentication handling, customizable by resource and request method
* Request throttling, customizable by resource and request method
* Request logging, including basic request data and request processing time
* Multiple API versions supported simultaneously
* Fully customizable response data serializer (JSON implemented by default)

##### To run/try:

1. Clone the repository
2. Make sure the requirements are satisfied
3. Execute runserver.py with Python (server runs on port 5000)
4. Navigate in the browser to "server_address:5000/v1/rest_example" and/or "server_address:5000/v2/rest_example"

##### To use/implement/extend:

* To implement a new RESTful resource in the API, simply create a class based on flask_rest.utils.restview.RestView, and implement the methods needed (get, post, put, delete)
* See flask_rest.example_api_v2.example_handler.ExampleHandler for more details on how to make a fully customized API resource
* To customize authentication, create the appropriate class based on CommonAuthorization in flask_rest.utils.auth (see flask_rest.utils.auth.ExampleAuthorization for more information), then specify the class in the resource handler's init method for the HTTP method wanted
* To customize throttling, create the appropriate class based on CommonThrottle in flask_rest.utils.throttle (see flask_rest.utils.throttle.StrictThrottle for more information), make an instance of the throttle, then use it in the resource handler's init method for the HTTP method wanted
* To add request logging, add the code to the marked section in the __log_request method in flask_rest.utils.restview.RestView
* To register/unregister resource for specific API versions, edit flask_rest.utils.router
* See flask_rest.utils.data_utils for details on how to add more data serializers
* See flask_rest.utils.http_utils for a list of recognized HTTP response names and codes