
from http.server import HTTPServer
from threading import Thread
from bot.FirmusPiett import FirmusPiett
from bot.TydiriumServer import startControllPanel, ControllPanel

HOST_NAME = ""
PORT = 7216
PIETT_TOKEN = ""


if __name__ == '__main__':
    server = HTTPServer((HOST_NAME, PORT), ControllPanel)
    server_thread = Thread(target=startControllPanel, args={server})
    server_thread.start()

    piett = FirmusPiett(HOST_NAME, PORT)
    piett.run(PIETT_TOKEN)

    server_thread.join()
