# Usage

**DoorStateTracker** should be started by `cron` (simplest variant is every day).
The script that cron should run may be similar to door_stats/example_data_gathering.sh
DoorStateTracker uses *sched* to schedule hour runs,
so I suggests to run cron a day earlier (about 23:00)
and schedule data gathering for the following day ( DATE=$(date --date="tomorrow" +%Y-%m-%d) ).

**DataAnalyzer** should run time to time to update the predictions on the server.
I thought about `cron` once a day to update the day of the week that just passed.
So cron should run something like door_stats/example_upload_predictions.sh every day (about 3:00 maybe).
