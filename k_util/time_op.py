import datetime
import pytz
import tzlocal

TZ_UTC = pytz.utc
TZ_LOCAL = tzlocal.get_localzone()


TIME_FORMAT_DEFAULT = '%Y-%m-%d %H:%M:%S.%f'
TIME_FORMAT_FOR_FILE = '%Y_%m_%d__%H_%M_%S_%f'


def get_time_str_now(time_format):
    date_time_obj = datetime.datetime.now()
    return convert_time_obj_to_time_str(date_time_obj, time_format)


def convert_time_obj_to_time_str(date_time_obj=None, time_format=TIME_FORMAT_DEFAULT):
    date_time_obj = date_time_obj or datetime.datetime.now()
    return date_time_obj.strftime(time_format)


def convert_time_str_to_time_obj(date_time_str, time_format=TIME_FORMAT_DEFAULT):
    return datetime.datetime.strptime(date_time_str, time_format)


def convert_time_zone(time_obj, tz_to, tz_from=None):
    tz_from = tz_from or time_obj.tzinfo
    if tz_from:
        time_obj = time_obj.replace(tzinfo=tz_from)
    else:
        if not time_obj.tzinfo:
            raise ValueError('tz_from is none.')
    time_obj = time_obj.astimezone(tz_to)
    return time_obj


def convert_time_zone_with_time_str(time_str, tz_to, tz_from=None, format_from=TIME_FORMAT_DEFAULT, format_to=None):
    format_to = format_to or format_from
    time_obj = datetime.datetime.strptime(time_str, format_from)
    tz_from = tz_from or time_obj.tzinfo
    if tz_from:
        time_obj = time_obj.replace(tzinfo=tz_from)
    else:
        if not time_obj.tzinfo:
            raise ValueError('tz_from is none.')
    time_obj = time_obj.astimezone(tz_to)
    time_str = time_obj.strftime(format_to)
    return time_str


def convert_time_str_format(time_str_src, t_format_src, t_format_dst):
    time_obj = datetime.datetime.strptime(time_str_src, t_format_src)
    return time_obj.strftime(t_format_dst)


