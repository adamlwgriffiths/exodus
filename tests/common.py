from __future__ import absolute_import, print_function


class TestObject(object):
    def __init__(self):
        self.a = 1


class AnotherObject(object):
    def __init__(self):
        self.a = 2


class DictAdapter(object):
    def __init__(self, data=None):
        self.db = data or {}

    @property
    def version(self):
        return self.db.get('version', None)

    @version.setter
    def version(self, version):
        self.db['version'] = version
