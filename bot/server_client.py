from datetime import datetime
import requests

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_door_state(host, port, timeout=10.0):
    request = requests.get(f"http://{host}:{port}/door-state", timeout=timeout)
    content = request.text.split('\n')
    door_state = int(content[0])
    last_update = datetime.strptime(content[1], DATE_FORMAT)
    return door_state, last_update


def get_door_state_prediction(host, port, timeout=10.0):
    request = requests.get(f"http://{host}:{port}/door-state-prediction", timeout=timeout)
    content = request.text.split('\n')
    door_state = int(content[0])
    return door_state
