from flask import Flask

app = Flask(__name__)
app.debug = True # Switch to False for production
app.config['MAX_CONTENT_LENGTH'] = 8388608 # Limit file upload to 8MB (8x1024x1024)

from flask_rest.utils.error_handlers import *
from flask_rest.utils.monitor_handlers import *
from flask_rest.utils.router import register_handlers

register_handlers('v1') # Register all resources in version 1 of the API
register_handlers('v2') # Register all resources in version 2 of the API