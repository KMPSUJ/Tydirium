from datetime import datetime
import requests

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_door_state(host, port):
    request = requests.get(f"http://{host}:{port}")
    content = request.text.split('\n')
    door_state = int(content[0])
    last_update = datetime.strptime(content[1], DATE_FORMAT)
    return door_state, last_update
