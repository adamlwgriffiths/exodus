from __future__ import print_function
from exodus import BaseMigration


class Migration(BaseMigration):
    version = '2015_10_10'

    def can_migrate_database(self, adapter):
        return self.version > adapter.db.get('version', None)

    def migrate_database(self, adapter):
        # migrate the keys
        adapter.db['c'] = adapter.db['a']
        del adapter.db['a']
        adapter.db['version'] = self.version
