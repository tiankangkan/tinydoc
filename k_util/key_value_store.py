import shelve
import os
from file_op import make_sure_file_dir_exists


class KVStoreShelve(object):
    def __init__(self, data_dir='', db_name=None, writeback=True):
        self.db_name = db_name or 'kv_database'
        self.file_path = os.path.join(data_dir, self.db_name)
        self.inst = None
        self.writeback = writeback
        self.make_db_open()

    def make_db_open(self):
        if self.inst is None:
            make_sure_file_dir_exists(self.file_path)
            self.inst = shelve.open(self.file_path, writeback=self.writeback)

    def close(self):
        if self.inst:
            self.inst.close()
        self.inst = None

    def put(self, key, value):
        self.make_db_open()
        self.inst[key] = value
        self.sync()

    def get(self, key):
        self.make_db_open()
        return self.inst[key]

    def sync(self):
        self.inst.sync()

    def __str__(self):
        self.make_db_open()
        return str(self.inst)


if __name__ == '__main__':
    kv = KVStoreShelve()
    c = ['apd, ''erty']
    kv.put('key', ['apd, ''erty'])
    print kv
    c.append('sdasas')
    kv.put('key', c)
    print kv