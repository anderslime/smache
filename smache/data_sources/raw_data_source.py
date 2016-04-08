class Raw:
    pass


class RawDataSource:
    @classmethod
    def is_instance(cls, value):
        return issubclass(value, Raw)

    def __init__(self, entity_class=None):
        self.data_source_id = 'raw_value'

    def for_entity_class(self, entity_class):
        return entity_class == Raw

    def serialize(self, raw_value):
        return raw_value

    def find(self, raw_value):
        return raw_value

    def subscribe(self, fun):
        pass
