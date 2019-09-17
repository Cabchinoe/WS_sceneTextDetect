#encoding=utf8
#from wsgiref.simple_server import make_server
import logging
import re
import app
class ServerClass:

    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s PID:%(process)d %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )
        logging.info( 'server init...')
        #do sth
        self.urls = [
            (r'/?$', app.index),
            (r'/sceneTextDetect', app.sceneTextDetect)
        ]
        logging.info( 'server is running')

    def __call__(self,environ, start_response):
        path = environ.get('PATH_INFO', '')
        for regex, callback in self.urls:
            match = re.match(regex, path)
            if match is not None:
                # func = globals()[callback]
                func = callback
                header = [('Content-type', 'text/plain')]
                return func(environ, start_response,header)
        status = '404 Not Found'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return '404 NOT FOUND!\n'


server = ServerClass()

