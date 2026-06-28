import os
import sys

# Add the parent directory to the path so we can import the btg package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from btg import create_app

app = create_app()

def handler(event, context):
    """Netlify serverless function handler."""
    # Convert Netlify event to Flask request
    from flask import Flask
    
    with app.request_context(event.get('httpMethod', 'GET'), event.get('path', '/')):
        # Set up environ
        environ = {
            'REQUEST_METHOD': event.get('httpMethod', 'GET'),
            'PATH_INFO': event.get('path', '/'),
            'QUERY_STRING': event.get('queryStringParameters', '') or '',
            'CONTENT_TYPE': event.get('headers', {}).get('content-type', ''),
            'CONTENT_LENGTH': event.get('headers', {}).get('content-length', '0'),
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '443',
            'HTTPS': 'on',
            'wsgi.input': event.get('body', ''),
            'wsgi.errors': sys.stderr,
            'wsgi.url_scheme': 'https',
        }
        
        # Add headers
        for key, value in event.get('headers', {}).items():
            key = key.upper().replace('-', '_')
            if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                environ[f'HTTP_{key}'] = value
        
        # Get response from Flask app
        response = app.full_dispatch_request()
        
        return {
            'statusCode': response.status_code,
            'headers': dict(response.headers),
            'body': response.get_data(as_text=True)
        }
