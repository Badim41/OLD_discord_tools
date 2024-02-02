import datetime


class Time_Count:
    def __init__(self):
        self.start_time = datetime.datetime.now()

    def count_time(self):
        end_time = datetime.datetime.now()
        spent_time = str(end_time - self.start_time)
        # убираем миллисекунды
        spent_time = spent_time[:spent_time.find(".")]
        if not "0:00:00" in str(spent_time):
            return spent_time
        raise "Прошло 0:00:00"