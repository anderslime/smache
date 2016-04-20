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

    data_source.disconnect()


def test_subscriber_is_notified_on_delete():
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

    user.delete()

    assert notified == {
        'notified_data_source': data_source,
        'notified_entity_id': user.id
    }

    data_source.disconnect()

def test_subscriber_is_notified_on_bulk_insert_with_load():
    data_source = MongoDataSource(User)

    user1 = User(name='Anders', age=12)
    user2 = User(name='Henrik', age=50)

    notified = {
        'notified_data_sources': [],
        'notified_entity_ids': []
    }

    def notify(data_source, entity):
        notified['notified_data_sources'].append(data_source)
        notified['notified_entity_ids'].append(str(entity.id))

    data_source.subscribe(notify)

    users = User.objects.insert([user1, user2])
    user_ids = [str(user.id) for user in users]

    assert notified == {
        'notified_data_sources': [data_source, data_source],
        'notified_entity_ids': user_ids
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
