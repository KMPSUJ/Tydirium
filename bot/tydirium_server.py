from http.server import BaseHTTPRequestHandler, HTTPServer
import sys
from threading import Thread
from datetime import datetime
# import cgi


HOST_NAME = ""
PORT = 7216
HTTP_TIMEOUT = 10  # in seconds
SERVER_LIFETIME = 300  # in seconds
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class ControllPanel(BaseHTTPRequestHandler):
    """
    Main HTTP server.
    Responsible for receiving posts from sensor (Tydirium)
    with current state of the door and providing this information
    to discord bot.
    """

    code_blue = -1
    # the type is always the same, easier to generate message
    last_update = datetime(1999, 12, 12, 12, 12, 12, 12)

    def do_POST(self): # pylint: disable=C0103
        print("I got POST")

        def accept_post():
            try:
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                # reads ONLY one byte (works as long as only one service is connecting)
                body = self.rfile.read(1)
                ControllPanel.code_blue = ControllPanel.parse_as_expected(body)
                ControllPanel.last_update = datetime.now()
                output = ""
                self.wfile.write(output.encode())
                print("Received code:", ControllPanel.code_blue)
            except:
                self.send_error(404, f"{sys.exc_info()[0]}")
                print(sys.exc_info())
        serve_thread = Thread(target=accept_post, args={})
        serve_thread.start()
        serve_thread.join(timeout=HTTP_TIMEOUT)

    def do_GET(self): # pylint: disable=C0103
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        message = self.generate_door_state_message()
        self.wfile.write(bytes(message, "utf8"))

    @staticmethod
    def parse_as_expected(body):
        body = str(body)
        if body[0] == 'b' and body[1] == body[-1] == '\'':
            return int(body[2:-1])
        return -1

    def generate_door_state_message(self) -> str:
        return str(self.code_blue) + "\n" + self.last_update.strftime(DATE_FORMAT)


def start_controll_panel(panel):
    print(f"Server started http://{HOST_NAME}:{PORT}")
    try:
        while True:
            thread = Thread(target=panel.serve_forever, name="Tydirium server")
            thread.start()
            thread.join(timeout=SERVER_LIFETIME)
            if thread.is_alive():
                panel.shutdown()
    except KeyboardInterrupt:
        panel.server_close()
        print("Server stopped.")


if __name__ == "__main__":
    server = HTTPServer((HOST_NAME, PORT), ControllPanel)
    start_controll_panel(server)
