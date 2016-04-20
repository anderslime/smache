import pytest

from smache.data_sources import DummyDataSource, DummyEntity
from smache.data_source_repository import DataSourceRepository, \
    DataSourceNotFound, DataSourceTypeNotFound


@pytest.yield_fixture
def entity():
    yield DummyEntity(1, 'hello')


@pytest.yield_fixture
def data_source():
    yield DummyDataSource(DummyEntity)


@pytest.yield_fixture
def repo(data_source):
    yield DataSourceRepository([data_source])


def test_finding_data_source_by_id(repo, data_source):
    assert repo.find_by_data_source_id('DummyEntity') == data_source


def test_finding_data_source_by_id_does_not_exist(repo):
    with pytest.raises(DataSourceNotFound):
        repo.find_by_data_source_id('NonExisting')


def test_finding_data_source_by_entity(monkeypatch, entity, data_source, repo):
    assert repo.find_by_entity(entity) == data_source


def test_finding_data_source_by_entity_does_not_exist(monkeypatch,
                                                      entity,
                                                      data_source,
                                                      repo):
    monkeypatch.setattr(data_source, 'for_entity', lambda e: False)

    with pytest.raises(DataSourceNotFound):
        repo.find_by_entity(entity)


def test_registering_data_source():
    def on_update():
        pass

    repo = DataSourceRepository([])

    assert len(repo._data_sources) == 0

    data_source = repo.find_or_register_data_source(DummyEntity, on_update)

    assert repo._data_sources[0] == data_source
    assert data_source.subscriber == on_update


def test_finding_data_source(repo):
    def on_update():
        pass

    assert len(repo._data_sources) == 1

    data_source = repo.find_or_register_data_source(DummyEntity, on_update)

    assert len(repo._data_sources) == 1
    assert data_source.subscriber != on_update


def test_exception_is_raised_when_unkown_entity_is_used(repo):
    class UnknownEntity:
        @classmethod
        def is_instance(cls, entity_class):
            return False

    with pytest.raises(DataSourceTypeNotFound):
        repo.find_or_register_data_source(UnknownEntity)
