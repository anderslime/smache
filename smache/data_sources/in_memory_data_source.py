class InMemoryEntity:
    data = {}
    subscribers = []

    @classmethod
    def update(cls, entity_id, value):
        serialized_id = str(entity_id)
        cls.data[serialized_id] = value
        for subscriber in cls.subscribers:
            subscriber(serialized_id)

    @classmethod
    def set_data(cls, new_data={}):
        cls.data = new_data

    @classmethod
    def unsubscribe_all(cls):
        cls.subscribers = []

    @classmethod
    def find(cls, input_value):
        raw_data = cls.data.get(cls._key(input_value))
        if raw_data:
            return cls(input_value, raw_data['value'])

    @classmethod
    def subscribe(cls, subscriber):
        cls.subscribers.append(subscriber)

    @classmethod
    def _key(self, input_value):
        if isinstance(input_value, int) or isinstance(input_value, str):
            return str(input_value)
        else:
            return input_value.id

    def __init__(self, id, value):
        self.id = id
        self.value = value
        self.data_source_id = self.__class__.__name__

        self.__class__.original_data = self.__class__.data.copy()


class InMemoryDataSource:

    @classmethod
    def data_source_id(cls, document):
        return document.__name__

    @classmethod
    def is_instance(cls, entity_class):
        return issubclass(entity_class, InMemoryEntity)

    def __init__(self, dummy_entity_class):
        self.dummy_entity_class = dummy_entity_class
        self.data_source_id = dummy_entity_class.__name__
        self.subscriber = lambda x, y: x

    def subscribe(self, fun):
        self.subscriber = fun
        self.dummy_entity_class.subscribe(self.did_update)

    def for_entity(self, entity_instance):
        return self.data_source_id == entity_instance.data_source_id

    def for_entity_class(self, document):
        return self.data_source_id == self.__class__.data_source_id(document)

    def did_update(self, entity_id):
        entity = self.dummy_entity_class.find(entity_id)
        if not entity:
            entity = self.dummy_entity_class(entity_id, None)
        self.subscriber(self, entity)

    def find(self, entity_id):
        return self.dummy_entity_class.find(entity_id)

    def serialize(self, dummy_entity):
        return dummy_entity.id
