from PyQt5.QtCore import QThread
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
import cv2
from os import curdir, sep
from filepaths import paths


class myHandler(BaseHTTPRequestHandler):

    # Handler for the GET requests
    def do_GET(self):
        if self.path == "/":
            self.path = r"./index.html"

        try:
            # Check the file extension required and
            # set the right mime type
            send_reply = False
            if self.path.endswith(".html"):
                mimetype = 'text/html'
                send_reply = True
            if self.path.endswith(".jpg"):
                mimetype = 'image/jpg'
                send_reply = True
            if self.path.endswith(".gif"):
                mimetype = 'image/gif'
                send_reply = True
            if self.path.endswith(".js"):
                mimetype = 'application/javascript'
                send_reply = True
            if self.path.endswith(".css"):
                mimetype = 'text/css'
                send_reply = True

            if send_reply:
                # Open the static file requested and send it
                f=open(curdir + sep + self.path, 'rb')
                self.send_response(200)
                self.send_header('Content-type', mimetype)
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
            return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)


class Server(QThread):
    def __init__(self, camera):
        super(QThread, self).__init__()
        self.camera = camera
        self.logger = logging.getLogger("Server")
        self.active = False

    def run(self):
        self.active = True
        # start server
        try:
            # Create a web server and define the handler to manage the
            # incoming request
            server = HTTPServer(('192.168.8.174', 8080), myHandler)
            self.logger.info("Started httpserver on port 8080")

        # Wait forever for incoming http requests
        # server.serve_forever()

        except KeyboardInterrupt:
            self.logger.info("^C received, shutting down the web server")
            server.socket.close()

        while self.active:
            if self.camera.capturing:
                cv2.imwrite(paths["database"] + "last_frame.jpg", self.camera.frame)
            server.handle_request()
