from http.server import BaseHTTPRequestHandler, HTTPServer
import sys
from threading import Thread
from multiprocessing import Process
from datetime import datetime
# import cgi


HOST_NAME = ""
PORT = 7216
HTTP_TIMEOUT = 10  # in seconds
SERVER_LIFETIME = 300  # in seconds
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class ControlPanel(BaseHTTPRequestHandler):
    """
    Main HTTP server.
    Responsible for receiving posts from sensor (Tydirium)
    with current state of the door and providing this information
    to discord bot.
    """

    code_blue = -1
    # the type is always the same, easier to generate message
    last_update = datetime(1999, 12, 12, 12, 12, 12, 12)
    predictions = dict()

    def do_POST(self): # pylint: disable=C0103
        print("I got POST")
        self.accept_post()

    def do_GET(self): # pylint: disable=C0103
        if self.path == "/door-state":
            message = bytes(self.generate_door_state_message(), "utf8")
        elif self.path == "/door-state-prediction":
            message = bytes(self.generate_door_state_prediction_message(), "utf8")
        else:
            message = bytes(f"The path {self.path} is unknown. Try /door-state", "utf8")
        self.respond_with_this_message(message)

    @staticmethod
    def parse_as_expected(body):
        body = str(body)
        if body[0] == 'b' and body[1] == body[-1] == '\'':
            return int(body[2:-1])
        return -1

    def generate_door_state_message(self) -> str:
        return str(self.code_blue) + "\n" + self.last_update.strftime(DATE_FORMAT)

    def generate_door_state_prediction_message(self) -> str:
        when = self.headers["Date-Time"]
        try:
            wanted_date = datetime.strptime(when, DATE_FORMAT)
            message = ControlPanel.predictions[(wanted_date.isoweekday(), wanted_date.hour)][wanted_date.minute]
        except:
            message = "-1"
        return message

    def respond_with_this_message(self, message: bytes):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header("Content-Length", str(len(message)))
        self.end_headers()
        self.wfile.write(message)

    def accept_post(self):
        try:
            if self.path == "/post/door-state-prediction":
                self.accept_new_door_state_predictions()
            else:
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                # checks the Content-Length and reads the whole message
                body = self.rfile.read(int(self.headers["Content-Length"]))
                ControlPanel.code_blue = ControlPanel.parse_as_expected(body)
                ControlPanel.last_update = datetime.now()
                output = ""
                self.wfile.write(output.encode())
                print("Received code:", ControlPanel.code_blue)
        except:
            self.send_error(404, f"{sys.exc_info()[0]}")
            print(sys.exc_info())

    def accept_new_door_state_predictions(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        week_day = int(self.headers["Day-Of-Week"])
        hour = int(self.headers["Hour"])
        # read passed date, convert to str, split on \n into a list, and grab first 60 elements
        predictions = str(self.rfile.read(int(self.headers["Content-Length"])))[2:].split(" ")[0:60]
        # update stored predictions
        ControlPanel.predictions[(week_day, hour)] = predictions
        # respond with success code
        output = f"{(week_day, hour)}"
        self.wfile.write(output.encode())
        print("Received predictions for :", (week_day, hour))


def start_control_panel(panel):
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
    server = HTTPServer((HOST_NAME, PORT), ControlPanel)
    start_control_panel(server)
