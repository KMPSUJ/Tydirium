from bot.server_client import get_door_state
from datetime import datetime, date, timedelta
from time import time, sleep
import sched
import numpy as np
from threading import Thread


class DoorStateTracker:
    host: str
    port: int
    door_state: int
    last_update: datetime
    data_validation_time = timedelta(seconds=300)

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def gather_hour_data(self, day: date, hour: int, output_dir_path) -> None:
        # check if a delay is needed before running
        # or if it isn't too late to start, up to 30 seconds too late is allowed
        time_to_start = self.time_left_to_start(day, hour)
        if time_to_start < -30:
            return None
        elif time_to_start > 0:
            sleep(time_to_start)
        # gather data
        data = np.full(60, -2)
        for i in range(60):
            star_time = time()
            # get new data and save them if valid
            self.door_state, self.last_update = get_door_state(self.host, self.port, timeout=10.0)
            if self.is_door_state_valid():
                data[i] = self.door_state
            else:
                data[i] = -1
            # wait about a minute
            time_so_sleep = 60.0 - (time() - star_time)
            if time_so_sleep < 0.0:
                raise RuntimeError
            sleep(time_so_sleep)
        # save gathered data
        file_name = self.generate_hour_file_name(day, hour)
        np.savetxt(f"{output_dir_path}/{file_name}", data, fmt='%i')

    def schedule_daily_runs(self, day: date, out_path, starting_hour=0, ending_hour=23) -> Thread:
        now = datetime.now()
        if now.date() > day:
            raise RuntimeError
        elif now.date() == day:
            starting_hour = max(starting_hour, now.hour)

        # schedule all events to start at correct time
        s = sched.scheduler(time, sleep)
        for hour in range(starting_hour, ending_hour+1):
            # if an event should have already started, schedule it to run immediately
            time_to_start = max(self.time_left_to_start(day, hour), 0.0)
            s.enter(time_to_start, 1, self.gather_hour_data, argument=(day, hour, out_path))

        th = Thread(target=self.run_scheduled_data_gathering, name="scheduled runs", args=(s,))
        th.start()
        return th

    def is_door_state_valid(self) -> bool:
        if datetime.now() - self.last_update < self.data_validation_time:
            return True
        return False

    @staticmethod
    def generate_hour_file_name(day: date, hour: int) -> str:
        if 0 <= hour < 24:
            file_name = f"{day.isoweekday()}_{str(hour).zfill(2)}_{day.isoformat()}.csv"
            return file_name
        return "incorrect.csv"

    @staticmethod
    def time_left_to_start(day: date, hour: int) -> float:
        now = datetime.now()
        when_to_start = datetime(year=day.year, month=day.month, day=day.day, hour=hour, minute=0, second=0)
        time_to_start = when_to_start - now
        return time_to_start.total_seconds()

    @staticmethod
    def run_scheduled_data_gathering(s: sched.scheduler) -> None:
        try:
            s.run()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    ds = DoorStateTracker("localhost", 7216)
    scheduled_data_gathering = ds.schedule_daily_runs(date.today(), "./data")
    scheduled_data_gathering.join()
