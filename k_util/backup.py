import os
import time
import re
import shutil

FILTER_ONE_DAY = lambda **para: para['modify'] > (para['now'] - 3600*24)
FILTER_ONE_WEEK = lambda **para: para['modify'] > (para['now'] - 3600*24*7)


dir_config_list = [
    dict(dir_path='/data/logs/custom/', filter_func=FILTER_ONE_DAY),
    dict(dir_path='/data/logs/error/', filter_func=FILTER_ONE_DAY),
]

dir_config_list_test = [
    dict(dir_path='/Users/kangtian/Documents/Master/paper_plane', filter_func=FILTER_ONE_DAY),
]


class FileBackup(object):
    def __init__(self, dir_config_list=None, to_dir=None):
        self.dir_config_list = dir_config_list or []
        self.to_dir = to_dir

    def add_dir_config(self, dir_path, filter_func):
        self.dir_config_list.append(dict(dir_path=dir_path, filter_func=filter_func))

    def gather_dir_files(self, dir_path, filter_func):
        res_list = list()
        for dir_path, dir_names, file_names in os.walk(dir_path):
            for file_name in file_names:
                # file_name = 'accessLog-2016-04-19__09.log'
                # m = re.match('.*?Log-(?P<year>.*?)-(?P<month>.*?)-(?P<day>.*?)__(?P<hour>.*?).log', file_name)
                # if m:
                #     r = m.groupdict()
                #     t_tuple = time.struct_time(r['year'], r['month'], r['day'], r['hour'])
                #     t_file = time.mktime(t_tuple)
                #     print r
                file_path = os.path.join(dir_path, file_name)
                modify_stamp = os.path.getmtime(file_path)
                need_backup = filter_func(modify=modify_stamp, now=time.time(), file_name=file_name)
                if need_backup:
                    res_list.append(file_path)
        return res_list

    def back_up(self):
        for config in self.dir_config_list:
            path_list = self.gather_dir_files(config['dir_path'], config['filter_func'])
            for file_path in path_list:
                print file_path
                file_name = os.path.basename(file_path)
                if self.to_dir:
                    to_file = os.path.join(self.to_dir, file_name)
                    if not os.path.exists(self.to_dir):
                        os.makedirs(self.to_dir)
                else:
                    to_file = file_path + '__backup'
                if os.path.isfile(to_file):
                    os.remove(to_file)
                shutil.copy(file_path, to_file)


if __name__ == '__main__':
    f = FileBackup(dir_config_list=dir_config_list, to_dir='/tmp/log_backup/')
    f.back_up()
