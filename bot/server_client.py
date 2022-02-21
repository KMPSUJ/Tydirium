from datetime import datetime
import requests

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class ServerClient:
    host: str
    port: int

    def __init__(self, host: str, port: int):
        if host == "":
            self.host = "localhost"
        else:
            self.host = host
        self.port = port

    def get_door_state(self, timeout=10.0):
        request = requests.get(f"http://{self.host}:{self.port}/door-state", timeout=timeout)
        content = request.text.split('\n')
        door_state = int(content[0])
        last_update = datetime.strptime(content[1], DATE_FORMAT)
        return door_state, last_update

    def get_door_state_prediction(self, timeout=10.0):
        request = requests.get(f"http://{self.host}:{self.port}/door-state-prediction", timeout=timeout)
        content = request.text.split('\n')
        door_state = int(content[0])
        return door_state
