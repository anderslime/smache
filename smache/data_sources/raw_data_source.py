class RawDataSource:
    def __init__(self):
        self.data_source_id = 'raw_value'

    def serialize(self, raw_value):
        return raw_value

    def find(self, raw_value):
        return raw_value

    def subscribe(self, fun):
        pass
