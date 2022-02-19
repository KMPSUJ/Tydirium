
from bot.server_client import get_door_state
from datetime import datetime, date, timedelta
from time import time, sleep
import sched
import numpy as np
from threading import Thread, enumerate

data_validation_time = timedelta(seconds=300)  # seconds
door_checking_period = 60  # seconds


class DoorStateTracker:
    host: str
    port: int
    door_state: int
    last_update: datetime

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def track_door_state(self):
        try:
            while True:
                self.door_state, self.last_update = get_door_state(self.host, self.port)
                sleep(door_checking_period - time() % door_checking_period)
        except KeyboardInterrupt:
            pass

    def gather_hour_data(self, output_dir_path):
        start_time = datetime.now()
        if 4 < start_time.minute < 55:
            return None
        data = np.full(60, -2)
        for i in range(60):
            if self.is_door_state_valid():
                data[i] = self.door_state
            else:
                data[i] = -1
            sleep(60 - time() % 60)
        file_name = self.generate_hour_file_name(start_time.date(), start_time.hour)
        np.savetxt(f"{output_dir_path}/{file_name}", data)

    def schedule_daily_runs(self, day: date, out_path, starting_hour=0) -> Thread:
        now = datetime.now()
        if now.date() > day:
            raise RuntimeError
        elif now.date() == day:
            starting_hour = max(starting_hour, now.hour)
        s = sched.scheduler(time, sleep)
        for hour in range(starting_hour, 24):
            action_start_time = datetime(year=day.year, month=day.month, day=day.day, hour=hour, minute=0, second=0)
            time_to_start = action_start_time - now
            s.enter(time_to_start.total_seconds(), 1, self.gather_hour_data, argument=(out_path,))
            print(hour)

        def run_data_gathering():
            try:
                s.run()
            except KeyboardInterrupt:
                pass
        th = Thread(target=run_data_gathering, name="scheduled runs")
        th.start()
        print("all running")
        return th

    def is_door_state_valid(self):
        if datetime.now() - self.last_update < data_validation_time:
            return True
        return False

    @staticmethod
    def generate_hour_file_name(day: date, hour: int) -> str:
        if 0 <= hour < 24:
            file_name = f"{day.isoweekday()}_{str(hour).zfill(2)}_{day.isoformat()}.csv"
            return file_name
        return "incorrect.csv"


def print_active_th():
    try:
        while True:
            print(enumerate())
            sleep(10)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    th_printing = Thread(target=print_active_th, name="thread printing")
    th_printing.start()

    ds = DoorStateTracker("localhost", 7216)
    door_tracking_thread = Thread(target=ds.track_door_state, name="Door state tracking")
    door_tracking_thread.start()
    scheduled_data_gathering = ds.schedule_daily_runs(date.today(), "./data")
    scheduled_data_gathering.join()
