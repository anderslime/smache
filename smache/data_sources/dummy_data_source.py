class DummyDataSource:
    def __init__(self, data_source_id):
        self.data_source_id = data_source_id
        self.subscriber = lambda x: x

    def subscribe(self, fun):
        self.subscriber = fun

    def did_update(self, entity_id):
        self.subscriber(self, entity_id)
