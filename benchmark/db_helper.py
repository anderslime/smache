from mongoengine import (Document, StringField, IntField, ListField,
                         ReferenceField)
from mongoengine.connection import connect, disconnect
from pymongo import MongoClient


class User(Document):
    name = StringField()
    age = IntField()


class Handin(Document):
    users = ListField(ReferenceField(User))
    score = IntField()


class TestSet:
    def __init__(self, db_alias, num_of_users, num_of_handins):
        self.db_alias = db_alias
        self.num_of_users = num_of_users
        self.num_of_handins = num_of_handins

    @property
    def num_of_users_per_handin(self):
        return self.num_of_users / self.num_of_handins


test_sets = [
    TestSet('small', 500, 20),
    TestSet('medium', 2500, 40),
    TestSet('large', 12500, 80),
    TestSet('humongous', 62500, 160)
]


def build_base_dbs():
    for test_set in test_sets:
        db_name = test_db_base_name(test_set.db_alias)
        db = connect(db_name)
        db.drop_database(db_name)

        print User._get_db()

        print "==== STARTING {} ====".format(test_set.db_alias)
        print "CREATING USERS"
        users = [User(name='Joe', age=25)
                 for _ in range(test_set.num_of_users)]
        User.objects.insert(users)

        print "BUILDING HANDINS"
        handins = [Handin(score=10)
                   for _ in range(test_set.num_of_handins)]

        print "APPENDING USERS TO HANDINS"
        handins = []
        users = User.objects()
        test_indices = range(0,
                             test_set.num_of_users,
                             test_set.num_of_users_per_handin)
        for i in test_indices:
            handins.append(
                Handin(
                    score=i,
                    users=users[i:i+test_set.num_of_users_per_handin]
                )
            )

        print "INSERTING HANDINS"
        Handin.objects.insert(handins)

        print "==== FINISHED {} ====".format(test_set.db_alias)

        disconnect('default')

        # Hack to avoid mongoengine caching connection
        User._collection = None
        Handin._collection = None


def restore_test_db(db_alias):
    client = MongoClient()
    client.admin.command(
        'copydb',
        fromdb=test_db_base_name(db_alias),
        todb=test_db_name(db_alias)
    )


def test_db_base_name(name):
    return "test_db_base_{}".format(name)


def test_db_name(name):
    return "test_db_{}".format(name)


def clean_dbs():
    for test_set in test_sets:
        clean_db(test_set.db_alias)


def clean_db(db_alias):
    db = connect_db(db_alias)
    db.drop_database(test_db_name(db_alias))

    restore_test_db(db_alias)


def connect_db_setup(db_name):
    def setup():
        connect_db(db_name)
    return setup


def connect_db(db_alias):
    disconnect('default')

    # Hack to avoid mongoengine caching connection
    User._collection = None
    Handin._collection = None

    return connect(test_db_name(db_alias))
