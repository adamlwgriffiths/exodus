

======
EXODUS
======

.. image:: https://travis-ci.org/someones/exodus.svg?branch=master
    :target: https://travis-ci.org/someones/exodus

Mass Migrations for all!

Exodus is a simple framework that allows you to define data migrations and apply
them to an entire data store, or individual objects.

Exodus does not know anything about your data store, instead each migration
provides the logic for accessing the data store.

The ability to migrate an entire data store, or a single object at a time, enable
Exodus to update data at read time, or through a batch process.

Exodus reads python files from a specified directory, migration objects are
automatically registered and sorted by version.

By not providing extensive abstractions, Exodus allows *you* to migrate your data
the way *you* want to. You won't have to fight Exodus.


How to Use
==========

Create a database migration module - './migrations' by default - and add a migration
file.
A specific filename format is not required, but it is recommended to use either
the current date, an incrementing number, or both, as the prefix followed by a short
description.

Eg:

* 2015_10_12_add_address_to_user.py
* 01_add_address_to_user.py, 02_add_rating_to_movie.py


A migration should inherit from BaseMigration and must define a number of variables
and methods::

    from exodus import BaseMigration

    class Migration(BaseMigration):
        # used to sort the migrations, recommended to use a string that matches
        # the filename's unique prefix.
        version = '2015_10_20'

        # an optional list of class name variables that are used to check if
        # an object should be migrated. These values should match the
        # class.__name__ value of the class / object to be migrated.
        # the logic that uses this can be modified by over-riding the
        # `can_migrate_object` method
        classes = ['TestObject']

        def can_migrate_database(self, adapter):
            '''Returns True if the database can be migrated, False otherwise.
            This function should use your own logic to check the database version
            or other 'signal' that the migration is appropriate for your database.
            '''
            return self.version > adapter['version']
    
        def migrate_database(self, adapter):
            '''Performs a full migration on the database.
            This can include moving or updating objects.
            For each object requiring a migration, the method `migrate_object` should
            be called.
            By default, migrate_object will look for a function matching `migrate_<class name>`.
            If the `classes` variable defines a class name, but there is no corresponding `migrate_<class name>`,
            an exception will be thrown on construction.
            Before calling `migrate_<class name>`, a check if made for a function matching
            the name `can_migrate_<class name>`, if found (it is entirely optional to define)
            it is called with the object as a parameter. If False, the migration is
            not performed.
            Ensure any migration version signals are set at the end of the function.
            '''
            adapter['objects'] = adapter['old_objects']
            del adapter['old_objects']
    
            for obj in adapter['objects']:
                self.migrate_object(obj)
            adapter['version'] = self.version
    
        def can_migrate_TestObject(self, obj):
            '''Called when an object of type TestObject is sent to `migrate_object`.
            Returns True if the migration should be applied to the object.
            This function is entirely optional. If not defined, the migration will be
            performed regardless.
            '''
            return obj.version < self.version
    
        def migrate_TestObject(self, obj):
            '''Performs a migration on the object.
            If the `classes` variable defines a class name, but there is no corresponding `migrate_<class name>`,
            an exception will be thrown on construction.
            Ensure any migration version signals are set at the end of the function.
            '''
            obj.my_value = obj.my_value + 1
            obj.version = self.version
            return obj


Overriding Migration Logic
==========================

At times the default migration logic is not appropriate.
The majority of the intelligence is located in the BaseMigration class to
allow you to over-ride logic whenever required.

For example, you could modify a Migration to work on serialised JSON data
rather than Python classes like so::

    class JsonMigration(BaseMigration):
        def can_migrate_object(self, obj):
            if not self.classes:
                return False
            # the class name is stored in the __class__ value of the dict
            obj = json.loads(obj)
            clsname = obj['__class__']
            return clsname in self.classes

        def migrate_object(self, obj):
            # load the string
            parsed = json.loads(obj)

            # get the object class name and dispatch to the appropriate function
            clsname = parsed['__class__']

            # check if we can migrate the object
            # this is an optional function
            func = self._can_migrate_object_func(clsname)
            if func:
                if not func(parsed):
                    return obj

            # perform the migration
            func = self._migrate_object_func(clsname)
            if func:
                parsed = func(parsed)
                # convert back to a string
                return json.dumps(parsed)

        def can_migrate_TestObject(self, obj):
            return obj['version'] < self.version

        def migrate_TestObject(self, obj):
            obj['my_value'] = obj['my_value'] + 1
            obj['version'] = self.version
            return obj

Authors
=======

* `Adam Griffiths <https://github.com/adamlwgriffiths>`_
