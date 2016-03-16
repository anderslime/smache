import tests.mongo_helper as mongo
from mongoengine.connection import connect, disconnect
from pymongo import MongoClient
from collections import namedtuple

test_sets = [
    ('small',     500,   20),  # = 25
    ('medium',    2500,  60),  # = 42
    ('large',     12500, 180), # = 69
    ('humongous', 62500, 540)  # = 116
]

test_db_names = [test_set[0] for test_set in test_sets]

def build_base_dbs():
    for name, num_of_users, num_of_handins, in test_sets:
        connect(test_db_base_name(name))

        print mongo.User._get_db()

        print "==== STARTING {} ====".format(name)
        print "CREATING USERS"
        users = [mongo.User(name='Joe', age=25) for _ in range(num_of_users)]
        mongo.User.objects.insert(users)

        print "BUILDING HANDINS"
        handins = [mongo.Handin(score=10) for _ in range(num_of_handins)]

        print "APPENDING USERS TO HANDINS"
        num_of_users_per_handin = num_of_users / num_of_handins
        handins = []
        users = mongo.User.objects()
        for i in range(0, num_of_handins, num_of_users_per_handin):
            handins.append(mongo.Handin(score=i, users=users[i:i+num_of_users_per_handin]))

        print "INSERTING HANDINS"
        mongo.Handin.objects.insert(handins)

        print "==== FINISHED {} ====".format(name)

        disconnect('default')

        # Hack to avoid mongoengine caching connection
        mongo.User._collection = None
        mongo.Handin._collection = None


def restore_test_db(db_name):
    client = MongoClient()
    client.admin.command(
        'copydb',
        fromdb=test_db_base_name(db_name),
        todb=test_db_name(db_name)
    )

def test_db_base_name(name):
    return "test_db_base_{}".format(name)

def test_db_name(name):
    return "test_db_{}".format(name)

def clean_and_connect_db(name):
    disconnect('default')

    # Hack to avoid mongoengine caching connection
    mongo.User._collection = None
    mongo.Handin._collection = None

    # Restore to base
    db_name = test_db_name(name)
    db = connect(db_name)
    db.drop_database(db_name)
    restore_test_db(name)

if __name__ == '__main__':
    build_base_dbs()
