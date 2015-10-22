from __future__ import absolute_import, print_function
import os
import re
import importlib
from blist import sortedlist
from .version import __version__


class sortedmigrationlist(sortedlist):
    def __init__(self, *args, **kwargs):
        kwargs['key'] = lambda x: x.version
        super(sortedmigrationlist, self).__init__(*args, **kwargs)


class Exodus(object):
    migrations = sortedmigrationlist()
    pattern = re.compile(r'^.+\.py$')

    @classmethod
    def register_migration(cls, migration):
        if migration not in cls.migrations:
            cls.migrations.add(migration)

    @classmethod
    def load_migrations(cls, path=None):
        if not cls.migrations:
            cls.migrations = sortedmigrationlist()

        path = path or 'migrations'

        # get a list of files in the path we've specified
        files = sorted(filter(cls.pattern.match, os.listdir(path)))

        module = path.replace('/', '.')
        strip_extension = lambda x: os.path.splitext(x)[0]
        path_to_module = lambda f: '.'.join([module, strip_extension(f)])
        import_file = lambda m: importlib.import_module(path_to_module(m))
        force_reload = lambda m: reload(m)

        # migrations will automatically register themselves at import time
        # force a reload, if we don't modules will never be re-imported and
        # thus will not run their meta class, and therefore not be re-registered
        # if we re-run the load_migrations method
        map(force_reload, map(import_file, files))

    @classmethod
    def can_migrate_database(cls, adapter):
        for migration in cls.migrations:
            if migration.can_migrate_database(adapter):
                return True
        return False

    @classmethod
    def migrate_database(cls, adapter):
        for migration in cls.migrations:
            if migration.can_migrate_database(adapter):
                migration.migrate_database(adapter)

    @classmethod
    def can_migrate_object(cls, obj):
        for migration in cls.migrations:
            if migration.can_migrate_object(obj):
                return True
        return False

    @classmethod
    def migrate_object(cls, obj):
        for migration in cls.migrations:
            if migration.can_migrate_object(obj):
                migration.migrate_object(obj)

    @classmethod
    def highest_version(cls):
        if cls.migrations:
            return cls.migrations[-1].version
        return None


class BaseMigrationMetaClass(type):
    def __new__(cls, clsname, bases, attrs):
        '''Automatically registers BaseMigration subclasses at class definition time.
        '''
        newclass = super(BaseMigrationMetaClass, cls).__new__(cls, clsname, bases, attrs)
        if newclass.__name__ is not 'BaseMigration':
            Exodus.register_migration(newclass())
        return newclass


class BaseMigration(object):
    __metaclass__ = BaseMigrationMetaClass

    classes = None
    version = None

    def __init__(self):
        # we must always have a version specified
        if not self.version:
            raise ValueError('Migration "{}" has no version specified'.format(self.__class__.__name__))

        # ensure we have a migration function for each object we support
        if self.classes:
            for clsname in self.classes:
                if not self._migrate_object_func(clsname):
                    raise ValueError('No migration function for class of type "{}", expected method called "{}"'.format(
                        clsname,
                        self._migrate_object_name(clsname)
                    ))

    def can_migrate_database(self, adapter):
        raise NotImplementedError('Must define can_migrate_database method')

    def can_migrate_object(self, obj):
        clsname = self.get_object_classname(obj)

        if not self.classes:
            return False

        if clsname not in self.classes:
            return False

        # check if we can migrate the object
        # this is an optional function
        func = self._can_migrate_object_func(clsname)
        if func:
            return func(obj)

        return True

    def get_object_classname(self, obj):
        return obj.__class__.__name__

    def migrate_database(self, adapter):
        raise NotImplementedError('Migration not implemented')

    def migrate_object(self, obj):
        clsname = self.get_object_classname(obj)

        # check if we can migrate the object
        # this is an optional function
        func = self._can_migrate_object_func(clsname)
        if func:
            if not func(obj):
                return obj

        # perform the migration
        func = self._migrate_object_func(clsname)
        if func:
            return func(obj)

        return obj

    def _can_migrate_object_name(self, clsname):
        return 'can_migrate_{}'.format(clsname)

    def _can_migrate_object_func(self, clsname):
        return getattr(self, self._can_migrate_object_name(clsname), None)

    def _migrate_object_name(self, clsname):
        return 'migrate_{}'.format(clsname)

    def _migrate_object_func(self, clsname):
        return getattr(self, self._migrate_object_name(clsname), None)

    def __lt__(self, other):
        return self.version < other.version

    def __le__(self, other):
        return self.version <= other.version

    def __eq__(self, other):
        return self.version == other.version

    def __ne__(self, other):
        return self.version != other.version

    def __gt__(self, other):
        return self.version > other.version

    def __ge__(self, other):
        return self.version >= other.version
