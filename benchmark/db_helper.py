from mongoengine import Document, StringField, IntField, connect, ListField, ReferenceField
from mongoengine.connection import connect, disconnect
from pymongo import MongoClient
from collections import namedtuple

class User(Document):
    name = StringField()
    age = IntField()

class Handin(Document):
    users = ListField(ReferenceField(User))
    score = IntField()

test_sets = [
    ('small',     500,   20),  # = 25
    ('medium',    2500,  60),  # = 42
    ('large',     12500, 180), # = 69
    ('humongous', 62500, 540)  # = 116
]

def build_base_dbs():
    for db_alias, num_of_users, num_of_handins, in test_sets:
        connect(test_db_base_name(db_alias))

        print User._get_db()

        print "==== STARTING {} ====".format(name)
        print "CREATING USERS"
        users = [User(name='Joe', age=25) for _ in range(num_of_users)]
        User.objects.insert(users)

        print "BUILDING HANDINS"
        handins = [Handin(score=10) for _ in range(num_of_handins)]

        print "APPENDING USERS TO HANDINS"
        num_of_users_per_handin = num_of_users / num_of_handins
        handins = []
        users = User.objects()
        for i in range(0, num_of_handins, num_of_users_per_handin):
            handins.append(Handin(score=i, users=users[i:i+num_of_users_per_handin]))

        print "INSERTING HANDINS"
        Handin.objects.insert(handins)

        print "==== FINISHED {} ====".format(name)

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
    for db_alias, _, _ in test_sets:
        clean_db(db_alias)

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

if __name__ == '__main__':
    build_base_dbs()
