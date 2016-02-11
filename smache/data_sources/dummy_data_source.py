from collections import namedtuple

DummyEntity = namedtuple('Entity', ['id', 'value'])

class DummyDataSource:
    def __init__(self, data_source_id, data = {}):
        self.data_source_id = data_source_id
        self.data = data
        self.subscriber = lambda x, y: x

    def subscribe(self, fun):
        self.subscriber = fun

    def did_update(self, entity_id):
        self.subscriber(self, entity_id)

    def update(self, id, value):
        self.data[str(id)] = value
        self.did_update(id)

    def find(self, id):
        raw_data = self.data[str(id)]
        return DummyEntity(id, raw_data['value'])
