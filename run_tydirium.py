import os
from http.server import HTTPServer
from threading import Thread
from bot.firmus_piett import FirmusPiett
from bot.tydirium_server import start_control_panel, ControlPanel

HOST_NAME = ""
PORT = 7216
PIETT_TOKEN = os.getenv('PIETT_TOKEN', "")


if __name__ == '__main__':
    server = HTTPServer((HOST_NAME, PORT), ControlPanel)
    server_thread = Thread(target=start_control_panel, args={server})
    server_thread.start()

    piett = FirmusPiett(HOST_NAME, PORT)
    piett.run(PIETT_TOKEN)

    server_thread.join()
