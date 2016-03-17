from smache.data_sources import MongoDataSource
from tests.mongo_helper import User, test_connect

import smache, pytest

test_connect()

@pytest.yield_fixture(autouse=True)
def reset_before_each_test():
    smache.reset_globals()
    yield

def teardown_module(module):
    smache.reset_globals()

def test_subscriber_is_notified_on_update():
    data_source = MongoDataSource(User)

    user = User(name='Anders', age=12)
    user.save()

    notified = {
        'notified_data_source': None,
        'notified_entity_id': None
    }

    def notify(data_source, entity):
        notified['notified_data_source'] = data_source
        notified['notified_entity_id'] = entity.id

    data_source.subscribe(notify)

    user.name = 'Emil'
    user.save()

    assert notified == {
        'notified_data_source': data_source,
        'notified_entity_id': user.id
    }

    data_source.disconnect()

def test_serialization():
    data_source = MongoDataSource(User)

    user = User(name='Anders', age=12)
    user.save()

    assert data_source.serialize(user) == str(user.id)

    data_source.disconnect()

def test_finding_record():
    data_source = MongoDataSource(User)

    user = User(name='Anders', age=12)
    user.save()

    assert data_source.find(str(user.id)) == user

    data_source.disconnect()

def test_data_source_id():
    data_source = MongoDataSource(User)
    assert data_source.data_source_id == 'User'
    data_source.disconnect()

def test_document():
    data_source = MongoDataSource(User)
    assert data_source.document == User
    data_source.disconnect()
