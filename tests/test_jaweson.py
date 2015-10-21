from __future__ import absolute_import, print_function
import unittest
import importlib
import json
from exodus import Exodus
from .common import DictAdapter
try:
    from jaweson import json as jaweson

    class TestObject(jaweson.Serialisable):
        def __init__(self):
            self.a = 1

    class AnotherObject(jaweson.Serialisable):
        def __init__(self):
            self.a = 2

    class TestJawesonMigration(unittest.TestCase):
        def setUp(self):
            Exodus.load_migrations('tests/jaweson_migrations')

            # import the migrations AFTER we initialise exodus
            self.migration1 = importlib.import_module('tests.jaweson_migrations.2015_03_10_add_b').Migration
            self.migration2 = importlib.import_module('tests.jaweson_migrations.2015_10_10_move_keys').Migration

        def tearDown(self):
            Exodus.migrations = None

        def test_migrations(self):
            adapter = DictAdapter({
                'a': [jaweson.dumps(TestObject()) for x in range(10)],
                'b': [jaweson.dumps(AnotherObject()) for x in range(5)],
            })

            tm1 = self.migration1()
            tm1.migrate_database(adapter)
            assert set(adapter.db.keys()) == set(['a', 'b', 'version'])
            assert len(filter(lambda obj: json.loads(obj)['a'] == 1, adapter.db['a'])) == len(adapter.db['a'])
            assert len(filter(lambda obj: json.loads(obj)['a'] == 2, adapter.db['b'])) == len(adapter.db['b'])
            assert len(filter(lambda obj: 'b' in json.loads(obj), adapter.db['a'])) == len(adapter.db['a'])
            assert len(filter(lambda obj: 'b' not in json.loads(obj), adapter.db['b'])) == len(adapter.db['b'])

            tm2 = self.migration2()
            tm2.migrate_database(adapter)
            assert set(adapter.db.keys()) == set(['b', 'c', 'version'])
            assert len(filter(lambda obj: json.loads(obj)['a'] == 1, adapter.db['c'])) == len(adapter.db['c'])
            assert len(filter(lambda obj: json.loads(obj)['b'] == 2, adapter.db['c'])) == len(adapter.db['c'])
            assert len(filter(lambda obj: json.loads(obj)['a'] == 2, adapter.db['b'])) == len(adapter.db['b'])
            assert len(filter(lambda obj: 'b' not in json.loads(obj), adapter.db['b'])) == len(adapter.db['b'])

        def test_manual_object_migration(self):
            tm1 = self.migration1()
            tm2 = self.migration2()

            a = json.loads(jaweson.dumps(TestObject()))
            assert 'b' not in a
            tm1.migrate_object(a)
            assert 'b' in a
            tm2.migrate_object(a)
            assert 'b' in a

            b = json.loads(jaweson.dumps(AnotherObject()))
            tm1.migrate_object(b)
            assert 'b' not in b
            tm2.migrate_object(b)
            assert 'b' not in b

        def test_object_migration(self):
            # individual migration
            a = json.loads(jaweson.dumps(TestObject()))
            assert 'b' not in a
            Exodus.migrate_object(a)
            assert 'b' in a

            b = json.loads(jaweson.dumps(AnotherObject()))
            assert 'b' not in b
            Exodus.migrate_object(b)
            assert 'b' not in b

        def test_exodus(self):
            adapter = DictAdapter({
                'a': [jaweson.dumps(TestObject()) for x in range(10)],
                'b': [jaweson.dumps(AnotherObject()) for x in range(5)],
            })

            Exodus.migrate_database(adapter)
            assert set(adapter.db.keys()) == set(['b', 'c', 'version'])
            assert len(filter(lambda obj: 'b' in obj, adapter.db['c'])) == len(adapter.db['c'])
            assert adapter.db['version'] == Exodus.highest_version()

except:
    pass
