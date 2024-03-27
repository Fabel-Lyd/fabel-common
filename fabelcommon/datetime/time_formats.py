from datetime import datetime, timedelta
import pytz


class TimeFormats:

    @staticmethod
    def get_date_time():
        time_gmt = datetime.utcnow()
        date_str = time_gmt.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
        mytime = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        mytime = mytime.replace(tzinfo=pytz.timezone('GMT'))
        return mytime.strftime("%a, %d %b %Y %H:%M:%S %Z")

    @staticmethod
    def get_date_time_string_utc(date_time: datetime) -> str:
        if not date_time.tzinfo:
            raise ValueError('Provided datetime object contains no time zone info')

        date_time_utc: datetime = date_time.astimezone(pytz.UTC)
        return date_time_utc.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

    @staticmethod
    def get_time_delta_hours(delta_hours):
        yesterday = datetime.now() - timedelta(hours=delta_hours)
        yesterday_formatted = yesterday.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        return yesterday_formatted

    @staticmethod
    def format_date_time_string(date_time):
        date_time_obj = datetime.strptime(date_time[:-6], '%Y-%m-%dT%H:%M:%S.%f')
        datetime_string = date_time_obj.strftime("%d.%m.%Y")
        return datetime_string

    @staticmethod
    def format_date_time_string_utc(date_time):
        date_time_obj = datetime.strptime(date_time[:-6], '%Y-%m-%dT%H:%M:%S.%f')
        utc_string = date_time_obj.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
        return utc_string

    @staticmethod
    def convert_to_minutes(duration):
        duration_split = duration.split(':')
        hours = duration_split[0]
        minutes = duration_split[1]
        if hours == '00':
            hours = '0'

        total_duration = int(hours) * 60 + int(minutes)
        return total_duration
