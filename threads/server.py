from PyQt5.QtCore import QThread
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
import cv2
from os import curdir, sep
from filepaths import paths
from utils.utils import add_text_to_image


class myHandler(BaseHTTPRequestHandler):

    # Handler for the GET requests
    def do_GET(self):
        if self.path == "/":
            self.path = r"/index.html"

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
            self.send_error(404, 'File Not Found... %s' % self.path)


class Server(QThread):
    def __init__(self, camera):
        super(QThread, self).__init__()
        self.camera = camera
        self.logger = logging.getLogger("Server")
        self.active = False
        self.server = None

    def run(self):
        self.active = True
        # start server
        try:
            # Create a web server and define the handler to manage the
            # incoming request
            self.server = HTTPServer(('192.168.8.174', 90), myHandler)
            self.logger.info("Started http server on port 90")

        # Wait forever for incoming http requests
        # server.serve_forever()

        except KeyboardInterrupt:
            self.logger.info("^C received, shutting down the web server")
            self.server.socket.close()

        while self.active:
            if self.camera.capturing:
                frame = add_text_to_image(
                    self.camera.frame,
                    self.camera.img_description,
                    top_left_xy=(0, 10),
                    font_scale=.7,
                    font_thickness=1,
                    font_color_rgb=(232, 162, 0),
                )
                cv2.imwrite(paths["database"] + "last_frame.jpg", frame)
            self.server.handle_request()

    def stop(self):
        self.logger.info("Thread was stopped")
        self.server.socket.close()
        self.active = False
        self.quit()
