
from http.server import BaseHTTPRequestHandler, HTTPServer
import sys
from threading import Thread
from datetime import datetime
# import cgi


HOST_NAME = ""
PORT = 7216
HTTP_TIMEOUT = 10  # in seconds
SERVER_LIFETIME = 300  # in seconds
date_format = "%Y-%m-%d %H:%M:%S"


class ControllPanel(BaseHTTPRequestHandler):
    code_blue = -1
    last_update = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #  self.code_blue = -1

    def do_POST(self):
        print("I got POST")

        def acceptPost():
            try:
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                #  ctype, pdict = cgi.parse_header(self.headers.get('Content-Type'))
                body = self.rfile.read(1)  # reads ONLY one byte (works as long as only one service is connecting)
                ControllPanel.code_blue = ControllPanel.parseAsExpected(body)
                ControllPanel.last_update = datetime.now()
                output = ""
                self.wfile.write(output.encode())
                print("Received code:", ControllPanel.code_blue)
            except:
                self.send_error(404, "{}".format(sys.exc_info()[0]))
                print(sys.exc_info())
        serveThread = Thread(target=acceptPost, args={})
        serveThread.start()
        serveThread.join(timeout=HTTP_TIMEOUT)

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        message = str(self.code_blue) + "\n" + self.last_update.strftime(date_format)
        self.wfile.write(bytes(message, "utf8"))

    @staticmethod
    def parseAsExpected(body):
        body = str(body)
        if body[0] == 'b' and body[1] == body[-1] == '\'':
            return int(body[2:-1])
        else:
            return -1


def startControllPanel(panel):
    print("Server started http://%s:%s" % (HOST_NAME, PORT))
    try:
        while True:
            th = Thread(target=panel.serve_forever)
            th.start()
            th.join(timeout=SERVER_LIFETIME)
    except KeyboardInterrupt:
        panel.server_close()
        print("Server stopped.")


if __name__ == "__main__":
    server = HTTPServer((HOST_NAME, PORT), ControllPanel)
    server_thread = Thread(target=startControllPanel, args={server})
    server_thread.start()

    server_thread.join()
