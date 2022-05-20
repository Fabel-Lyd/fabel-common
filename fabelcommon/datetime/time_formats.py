from datetime import datetime, timedelta


class TimeFormats():
    def __init__(self):
        pass

    def get_time_delta_hours(self, delta_hours):
        yesterday = datetime.now() - timedelta(hours=delta_hours)
        yesterday_formatted = yesterday.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        return yesterday_formatted

    def format_date_time_string(self, date_time):
        date_time_obj = datetime.strptime(date_time[:-6], '%Y-%m-%dT%H:%M:%S.%f')
        datetime_string = date_time_obj.strftime("%d.%m.%Y")
        return datetime_string

    def format_date_time_string_utc(self, date_time):
        date_time_obj = datetime.strptime(date_time[:-6], '%Y-%m-%dT%H:%M:%S.%f')
        utc_string = date_time_obj.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
        return utc_string

    def convert_to_minutes(self, duration):
        duration_split = duration.split(':')
        hours = duration_split[0]
        minutes = duration_split[1]
        if hours == '00':
            hours = '0'

        total_duration = int(hours) * 60 + int(minutes)
        return total_duration
