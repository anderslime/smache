from collections import namedtuple


class DummyEntity:
    data = {}
    subscribers = []

    @classmethod
    def update(cls, entity_id, value):
        serialized_id = str(entity_id)
        cls.data[serialized_id] = value
        for subscriber in cls.subscribers:
            subscriber(serialized_id)

    @classmethod
    def find(cls, entity_id):
        return cls.data.get(entity_id)

    @classmethod
    def subscribe(cls, subscriber):
        cls.subscribers.append(subscriber)

    def __init__(self, id, value):
        self.id = id
        self.value = value
        self.data_source_id = self.__class__.__name__

    @property
    def __name__(self):
        return self.data_source_id


class DummyDataSource:

    @classmethod
    def is_instance(cls, entity_class):
        return issubclass(entity_class, DummyEntity)

    def __init__(self, dummy_entity_class):
        self.dummy_entity_class = dummy_entity_class
        self.data_source_id = dummy_entity_class.__name__
        self.subscriber = lambda x, y: x

    def subscribe(self, fun):
        self.subscriber = fun
        self.dummy_entity_class.subscribe(self.did_update)

    def for_entity(self, entity_instance):
        return self.data_source_id == entity_instance.data_source_id

    def did_update(self, entity_id):
        entity = self.find(entity_id)
        if not entity:
            entity = self.dummy_entity_class(entity_id, None)
        self.subscriber(self, entity)

    def serialize(self, dummy_entity):
        return dummy_entity.id

    def find(self, input_value):
        raw_data = self.dummy_entity_class.find(self._key(input_value))
        if raw_data:
            return self.dummy_entity_class(input_value, raw_data['value'])

    def _key(self, input_value):
        if isinstance(input_value, int) or isinstance(input_value, str):
            return str(input_value)
        else:
            return input_value.id
