from threading import Thread
from door_stats.door_tracker import DoorStateTracker
from datetime import date
import sys
from door_stats.analyse_data import DataAnalyzer


def parse_args() -> tuple:
    host = "localhost"
    port = 7216
    data_path = "./data"

    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    if len(sys.argv) > 3:
        data_path = sys.argv[3]

    return host, port, data_path


if __name__ == '__main__':
    """
    Args should be passed in the following order:
        HOST PORT OUTPUT_PATH
    If some further arguments are missing, defaults are used:
    HOST=localhost, PORT=7216, OUTPUT_PATH=./data
    """
    host_name, port_num, data_directory_path = parse_args()
    data_analyzer = DataAnalyzer(host_name, port_num)
    data_analyzer.make_and_post_predictions_for_yesterday(data_directory_path)
