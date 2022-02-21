import numpy as np
from bot.server_client import ServerClient
from os import listdir
from os.path import join, isfile
from datetime import date, timedelta


class DataAnalyzer(ServerClient):

    def make_and_post_weekly_predictions(self, dir_path, n_weeks=4):
        for week_day in range(1, 8):
            for hour in range(24):
                pred = self.make_recent_predictions(dir_path, week_day, hour, n_weeks)
                self.post_door_state_prediction(week_day, hour, pred)

    def make_and_post_predictions_for_yesterday(self, dir_path, n_weeks=4):
        yesterday = date.today().isoweekday() - 1
        if yesterday == 0:
            yesterday = 7
        for hour in range(24):
            pred = self.make_recent_predictions(dir_path, yesterday, hour, n_weeks)
            self.post_door_state_prediction(yesterday, hour, pred)
    
    def make_and_post_predictions_valid_for_given_day(self, dir_path, for_when: date, n_weeks=4):
        for hour in range(24):
            files = self.get_list_of_files(dir_path, for_when.isoweekday(), hour, n_weeks, for_when)
            pred = self.make_predictions_for_given_file_list(files)
            self.post_door_state_prediction(for_when.isoweekday(), hour, pred)

    @staticmethod
    def make_recent_predictions(dir_path, day_of_week: int, hour: int, n_weeks) -> np.ndarray:
        file_list = DataAnalyzer.get_recent_files(dir_path, day_of_week, hour, n_weeks)
        return DataAnalyzer.make_predictions_for_given_file_list(file_list)

    # given a file list returns the prediction for that particular hour
    @staticmethod
    def make_predictions_for_given_file_list(file_list: list) -> np.ndarray:
        all_data = np.zeros((60, len(file_list)), dtype='int32')
        for i in range(len(file_list)):
            all_data[:, i] = np.loadtxt(file_list[i], dtype='int32')
        output = np.zeros(60)
        for i in range(60):
            this_hour_data = all_data[i, :]
            output[i] = np.mean(this_hour_data[this_hour_data >= 0])
        # if all data for a given point was missing, replace np.nan with -1.0
        output[np.isnan(output)] = -1.0
        return output

    # finds the date of last day_of_week, returns ref_date if day of week is correct
    @staticmethod
    def get_last_day_of_week(ref_date: date, day_of_week: int) -> date:
        days_diff = ref_date.isoweekday() - day_of_week
        if days_diff < 0:
            days_diff = 7 - days_diff
        return ref_date - timedelta(days=days_diff)

    # methods to find wanted file paths
    @staticmethod
    def get_recent_files(dir_path, day_of_week: int, hour: int, n_weeks: int) -> list:
        return DataAnalyzer.get_list_of_files(dir_path, day_of_week, hour, n_weeks, date.today())

    @staticmethod
    def get_list_of_files(dir_path, day_of_week: int, hour: int, n_weeks: int, ref_date: date) -> list:
        last_date = DataAnalyzer.get_last_day_of_week(ref_date, day_of_week) - timedelta(days=7*n_weeks)

        day_of_week = str(day_of_week)
        hour = str(hour).zfill(2)
        interesting_files = []
        for i in listdir(dir_path):
            if not isfile(join(dir_path, i)):
                continue
            # first check if day of week and hour matches, then check if date is ok
            if i.startswith(f"{day_of_week}_{hour}_"):
                if last_date <= date(*(int(j) for j in i[5:15].split('-'))) <= ref_date:
                    interesting_files.append(join(dir_path, i))
        return interesting_files

    @staticmethod
    def get_list_of_all_files(dir_path, day_of_week: int, hour: int) -> list:
        day_of_week = str(day_of_week)
        hour = str(hour).zfill(2)
        interesting_files = []
        for i in listdir(dir_path):
            if not isfile(join(dir_path, i)):
                continue
            if i.startswith(f"{day_of_week}_{hour}_"):
                interesting_files.append(join(dir_path, i))
        return interesting_files


if __name__ == '__main__':
    data_analyzer = DataAnalyzer("localhost", 7216)
    data_analyzer.make_and_post_predictions_for_yesterday("./data", n_weeks=4)
