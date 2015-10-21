from __future__ import print_function
import json
from exodus import BaseMigration


class Migration(BaseMigration):
    classes = ['TestObject']
    version = '2015_09_10'

    def can_migrate_database(self, adapter):
        return self.version > adapter.db.get('version', None)

    def get_object_classname(self, obj):
        return obj['__class__']

    def migrate_database(self, adapter):
        # migrate the objects
        for index, obj in enumerate(adapter.db['a']):
            j = json.loads(obj)
            self.migrate_object(j)
            obj = json.dumps(j)
            adapter.db['a'][index] = obj
        adapter.db['version'] = self.version

    def can_migrate_TestObject(self, obj):
        if 'b' in obj:
            return False
        return True

    def migrate_TestObject(self, obj):
        obj['b'] = 2
        return obj
