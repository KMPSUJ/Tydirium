from threading import Thread
from door_stats.door_tracker import DoorStateTracker
from datetime import date
import sys


def run_daily_door_state_gathering(day: date, host: str, port: int, out_path: str) -> None:
    ds = DoorStateTracker(host, port)
    scheduled_data_gathering = ds.schedule_daily_runs(day, out_path)
    scheduled_data_gathering.join()


def parse_args() -> tuple:
    day = date.today()
    host = "localhost"
    port = 7216
    out_path = "./data"

    if len(sys.argv) > 1:
        day = date(*(int(i) for i in sys.argv[1].split('-')))
    if len(sys.argv) > 2:
        host = sys.argv[2]
    if len(sys.argv) > 3:
        port = int(sys.argv[3])
    if len(sys.argv) > 4:
        out_path = sys.argv[4]

    return day, host, port, out_path


if __name__ == '__main__':
    """
    Args should be passed in the following order:
        DAY HOST PORT OUTPUT_PATH
    DAY format should be %Y-%m-%d
    If some further arguments are missing, defaults are used:
    DAY = today, HOST=localhost, PORT=7216, OUTPUT_PATH=./data
    """
    when, host_name, port_num, output_path = parse_args()
    run_daily_door_state_gathering(when, host_name, port_num, output_path)
