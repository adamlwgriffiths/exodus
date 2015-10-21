from __future__ import absolute_import, print_function
import unittest
import importlib
from exodus import Exodus, BaseMigration
from .common import TestObject, AnotherObject, DictAdapter


class TestMigration(unittest.TestCase):
    def setUp(self):
        Exodus.load_migrations('tests/migrations')

        # import the migrations AFTER we initialise exodus
        self.migration1 = importlib.import_module('tests.migrations.2015_03_10_add_b').Migration
        self.migration2 = importlib.import_module('tests.migrations.2015_10_10_move_keys').Migration

    def tearDown(self):
        Exodus.migrations = None

    def test_register_migrations(self):
        assert Exodus.migrations is not None
        assert len(Exodus.migrations) == 2
        migrations = map(lambda x: x.version, Exodus.migrations)
        assert self.migration1.version in migrations
        assert self.migration2.version in migrations

    def test_migrations(self):
        adapter = DictAdapter({
            'a': [TestObject() for x in range(10)],
            'b': [AnotherObject() for x in range(5)],
        })

        tm1 = self.migration1()
        tm1.migrate_database(adapter)
        assert set(adapter.db.keys()) == set(['a', 'b', 'version'])
        assert len(filter(lambda obj: obj.a == 1, adapter.db['a'])) == len(adapter.db['a'])
        assert len(filter(lambda obj: obj.a == 2, adapter.db['b'])) == len(adapter.db['b'])
        assert len(filter(lambda obj: hasattr(obj, 'b'), adapter.db['a'])) == len(adapter.db['a'])
        assert len(filter(lambda obj: not hasattr(obj, 'b'), adapter.db['b'])) == len(adapter.db['b'])

        tm2 = self.migration2()
        tm2.migrate_database(adapter)
        assert set(adapter.db.keys()) == set(['b', 'c', 'version'])
        assert len(filter(lambda obj: obj.a == 1, adapter.db['c'])) == len(adapter.db['c'])
        assert len(filter(lambda obj: obj.b == 2, adapter.db['c'])) == len(adapter.db['c'])
        assert len(filter(lambda obj: obj.a == 2, adapter.db['b'])) == len(adapter.db['b'])
        assert len(filter(lambda obj: not hasattr(obj, 'b'), adapter.db['b'])) == len(adapter.db['b'])

    def test_manual_object_migration(self):
        tm1 = self.migration1()
        tm2 = self.migration2()

        a = TestObject()
        tm1.migrate_object(a)
        assert hasattr(a, 'b')
        tm2.migrate_object(a)
        assert hasattr(a, 'b')

        b = AnotherObject()
        tm1.migrate_object(b)
        assert not hasattr(b, 'b')
        tm2.migrate_object(b)
        assert not hasattr(b, 'b')

    def test_object_migration(self):
        # individual migration
        a = TestObject()
        Exodus.migrate_object(a)
        assert hasattr(a, 'b')

        b = AnotherObject()
        Exodus.migrate_object(b)
        assert not hasattr(b, 'b')

    def test_migration_missing_method(self):
        with self.assertRaises(ValueError):
            class BrokenMigration(BaseMigration):
                classes = ['TestObject']
                version = '2015_10_10'

    def test_exodus(self):
        adapter = DictAdapter({
            'a': [TestObject() for x in range(10)],
            'b': [AnotherObject() for x in range(5)],
        })

        Exodus.migrate_database(adapter)
        assert set(adapter.db.keys()) == set(['b', 'c', 'version'])
        assert len(filter(lambda obj: hasattr(obj, 'b'), adapter.db['c'])) == len(adapter.db['c'])
        assert adapter.db['version'] == Exodus.highest_version()
