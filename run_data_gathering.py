from threading import Thread
from door_stats.door_tracker import DoorStateTracker, print_active_th
from datetime import date

if __name__ == '__main__':
    th_printing = Thread(target=print_active_th, name="thread printing")
    th_printing.start()

    ds = DoorStateTracker("localhost", 7216)
    door_tracking_thread = Thread(target=ds.track_door_state, name="Door state tracking")
    door_tracking_thread.start()
    scheduled_data_gathering = ds.schedule_daily_runs(date.today(), "./data")
    scheduled_data_gathering.join()
