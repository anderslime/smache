from collections import namedtuple

class DummyEntity:
    def __init__(self, data_source_id, id, value):
        self.data_source_id = data_source_id
        self.id             = id
        self.value          = value

    @property
    def __name__(self):
        return self.data_source_id

class DummyDataSource:
    def __init__(self, data_source_id, data = {}):
        self.data_source_id = data_source_id
        self.original_data = data.copy()
        self.data = data
        self.subscriber = lambda x, y: x

    def subscribe(self, fun):
        self.subscriber = fun

    def did_update(self, entity_id):
        entity = self.find(entity_id)
        if not entity:
            entity = DummyEntity(self.data_source_id, entity_id, None)
        self.subscriber(self, entity)

    def update(self, id, value):
        self.data[str(id)] = value
        self.did_update(id)

    def serialize(self, dummy_entity):
        return dummy_entity.id

    def find(self, input_value):
        raw_data = self.data.get(self._key(input_value))
        if raw_data:
            return DummyEntity(self.data_source_id, input_value, raw_data['value'])

    def reset(self):
        self.data = self.original_data.copy()

    def _key(self, input_value):
        if isinstance(input_value, int) or isinstance(input_value, str):
            return str(input_value)
        else:
            return input_value.id
