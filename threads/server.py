from PyQt5.QtCore import QThread
import logging
from http.server import BaseHTTPRequestHandler,HTTPServer
import cv2
from os import curdir, sep
from filepaths import paths

class myHandler(BaseHTTPRequestHandler):
	
	#Handler for the GET requests
	def do_GET(self):
		if self.path=="/":
			self.path=r"./index.html"

		try:
			#Check the file extension required and
			#set the right mime type

			sendReply = False
			if self.path.endswith(".html"):
				mimetype='text/html'
				sendReply = True
			if self.path.endswith(".jpg"):
				mimetype='image/jpg'
				sendReply = True
			if self.path.endswith(".gif"):
				mimetype='image/gif'
				sendReply = True
			if self.path.endswith(".js"):
				mimetype='application/javascript'
				sendReply = True
			if self.path.endswith(".css"):
				mimetype='text/css'
				sendReply = True

			if sendReply == True:
				#Open the static file requested and send it
				f = open(curdir + sep + self.path, 'rb') 
				self.send_response(200)
				self.send_header('Content-type',mimetype)
				self.end_headers()
				self.wfile.write(f.read())
				f.close()
			return

		except IOError:
			self.send_error(404,'File Not Found: %s' % self.path)
            
class Server(QThread):
    def __init__(self,camera):
        super(QThread,self).__init__()
        self.camera = camera
        self.logger = logging.getLogger(__name__)
        self.ThreadActive = False
        
    def run(self):    
        self.ThreadActive = True
        #start server
        try:
        	#Create a web server and define the handler to manage the
        	#incoming request
        	server = HTTPServer(('192.168.0.245', 8080), myHandler)
        	self.logger.info("Started httpserver on port 8080")
        	
        	#Wait forever for incoming htto requests
        	# server.serve_forever()

        except KeyboardInterrupt:
            self.logger.info("^C received, shutting down the web server")
            server.socket.close()
            
        while self.ThreadActive:
            if self.camera.capturing:
                cv2.imwrite(paths["database"] + "last_frame.jpg", self.camera.frame)
            server.handle_request()