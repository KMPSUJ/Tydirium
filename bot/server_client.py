
import requests
from datetime import datetime

date_format = "%Y-%m-%d %H:%M:%S"


def get_door_state(host, port):
    r = requests.get("http://%s:%s" % (host, port))
    content = r.text.split('\n')
    door_state = int(content[0])
    last_update = datetime.strptime(content[1], date_format)
    return door_state, last_update
