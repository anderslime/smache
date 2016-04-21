from .data_sources import InMemoryDataSource, RawDataSource, MongoDataSource


class DataSourceNotFound(Exception):
    pass


class DataSourceTypeNotFound(Exception):
    pass


class DataSourceRepository:
    def __init__(self, data_sources):
        self._data_sources = data_sources
        self._known_data_source_types = [
            RawDataSource,
            InMemoryDataSource,
            MongoDataSource
        ]

    def find_by_data_source_id(self, data_source_id):
        for data_source in self._data_sources:
            if data_source.data_source_id == data_source_id:
                return data_source
        raise DataSourceNotFound(
            "No data source for id={}".format(data_source_id)
        )

    def find_by_entity(self, entity):
        for data_source in self._data_sources:
            if data_source.for_entity(entity):
                return data_source
        raise DataSourceNotFound("No data source for entity={}".format(entity))

    def find_or_register_data_source(self, entity_class, on_update=None):
        data_source = self._find_by_entity_class(entity_class)
        if data_source is not None:
            return data_source
        else:
            return self._register_data_source(entity_class, on_update)

    def _register_data_source(self, entity_class, on_update):
        if self._find_by_entity_class(entity_class) is None:
            data_source_class = self._type_for_entity_class(entity_class)
            data_source = data_source_class(entity_class)
            self._data_sources.append(data_source)
            data_source.subscribe(on_update)
            return data_source

    def _find_by_entity_class(self, entity_class):
        for data_source in self._data_sources:
            if data_source.for_entity_class(entity_class):
                return data_source

    def _type_for_entity_class(self, entity_class):
        for data_source_class in self._known_data_source_types:
            if data_source_class.is_instance(entity_class):
                return data_source_class
        raise DataSourceTypeNotFound(
            "No data source type for {}".format(entity_class)
        )
