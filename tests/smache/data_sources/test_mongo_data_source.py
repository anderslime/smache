from smache.data_sources import MongoDataSource
from tests.mongo_helper import User, test_connect

test_connect()

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

def test_serialization():
    data_source = MongoDataSource(User)

    user = User(name='Anders', age=12)
    user.save()

    assert data_source.serialize(user) == str(user.id)

def test_finding_record():
    data_source = MongoDataSource(User)

    user = User(name='Anders', age=12)
    user.save()

    assert data_source.find(str(user.id)) == user

def test_data_source_id():
    assert MongoDataSource(User).data_source_id == 'User'

def test_document():
    assert MongoDataSource(User).document == User
