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

    def get_door_state_prediction(self, when: datetime, timeout=10.0):
        header = {"Date-Time": when.strftime(DATE_FORMAT)}
        request = requests.get(f"http://{self.host}:{self.port}/door-state-prediction", headers=header, timeout=timeout)
        door_state = float(request.text)
        return door_state

    def get_door_state_prediction_for_now(self, timeout=10.0):
        return self.get_door_state_prediction(datetime.now(), timeout=timeout)

    def post_door_state_prediction(self, day_of_week: int, hour: int, data_array, timeout=10.0):
        # data should be passed as a 1d-array that can be accessed by data_array[i]
        # each element of data_array should be a float, support por round function is needed
        message = ""
        for i in range(60):
            message += f"{round(data_array[i], ndigits=3)} "
        headers = {"Day-Of-Week": str(day_of_week), "Hour": str(hour)}
        requests.post(f"http://{self.host}:{self.port}/post/door-state-prediction", data=message, headers=headers,
                      timeout=timeout)
