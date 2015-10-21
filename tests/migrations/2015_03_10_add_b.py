from __future__ import print_function
from exodus import BaseMigration


class Migration(BaseMigration):
    classes = ['TestObject']
    version = '2015_09_10'

    def can_migrate_database(self, adapter):
        return self.version > adapter.db.get('version', None)

    def migrate_database(self, adapter):
        # migrate the objects
        for obj in adapter.db['a']:
            self.migrate_object(obj)
        adapter.db['version'] = self.version

    def can_migrate_TestObject(self, obj):
        if hasattr(obj, 'b'):
            return False
        return True

    def migrate_TestObject(self, obj):
        obj.b = 2
        return obj
