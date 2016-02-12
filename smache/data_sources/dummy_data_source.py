from collections import namedtuple

DummyEntity = namedtuple('Entity', ['id', 'value'])

class DummyDataSource:
    def __init__(self, data_source_id, data = {}):
        self.data_source_id = data_source_id
        self.original_data = data.copy()
        self.data = data
        self.subscriber = lambda x, y: x

    def subscribe(self, fun):
        self.subscriber = fun

    def did_update(self, entity_id):
        self.subscriber(self, entity_id)

    def update(self, id, value):
        self.data[str(id)] = value
        self.did_update(id)

    def find(self, input_value):
        raw_data = self._get(input_value)
        return DummyEntity(id, raw_data['value'])

    def reset(self):
        self.data = self.original_data.copy()

    def _get(self, input_value):
        if isinstance(input_value, int) or isinstance(input_value, str):
            return self.data[str(input_value)]
        else:
            return self.data[input_value.id]
