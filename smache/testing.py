import sys
import smache
from pymongo.cursor import Cursor


class RelationMissingError(Exception):
    pass


class DetectorYield:
    def __init__(self, detector, computed_fun):
        self.detector = detector
        self.computed_fun = computed_fun

    def __enter__(self):
        self.detector.start_detecting(self.computed_fun)

    def __exit__(self, type, value, traceback):
        if self.detector.has_anything_to_report():
            self.detector.print_report()
            raise RelationMissingError(
                "One of the smache computed functions are using data without "
                "subscribing to it"
            )
        else:
            self.detector.cleanup()


class RelationDetector:
    def __init__(self, documents, monkeypatch):
        self.documents = documents
        self.detected_collections = set()
        self.monkeypatch = monkeypatch

    def mark_as_detected(self, collection):
        self.detected_collections.add(collection)

    def has_anything_to_report(self):
        collection_diff = self._collection_diff()
        return len(collection_diff) > 0

    def print_report(self):
        computed_fun = smache._instance._computed_repo.get(self.computed_fun)
        if self.has_anything_to_report():
            print "WARNING: The computed function {} used data from the collections '{}' without subscribing to it".format(
                computed_fun.fun.__name__,
                self._collection_diff_names()
            )

    def _collection_diff(self):
        computed_fun = smache._instance._computed_repo.get(self.computed_fun)
        collections = self._collections(computed_fun.arg_deps) \
            + self._collections(computed_fun.data_source_deps) \
            + self._collections([ds for ds, _ in computed_fun.relation_deps])
        return self.detected_collections - set(collections)

    def _collection_diff_names(self):
        return ', '.join(set([col.name for col in self._collection_diff()]))

    def _collections(self, data_sources):
        return [data_source.document._get_collection()
                for data_source in data_sources]

    def start_detecting(this_detector, computed_fun):
        this_detector.computed_fun = computed_fun
        old_init = Cursor.__init__
        this_detector._old_cursor_init = old_init
        def new_init(cursor_self, *args, **kwargs):
            collection = args[0]
            this_detector.mark_as_detected(collection)
            return old_init(cursor_self, *args, **kwargs)

        this_detector.monkeypatch.setattr(Cursor, '__init__', new_init)

    def cleanup(this_detector):
        this_detector.monkeypatch.setattr(Cursor, '__init__', this_detector._old_cursor_init)

if 'pytest' in sys.modules:
    import pytest

    @pytest.yield_fixture
    def relation_detector(monkeypatch):
        detector = RelationDetector([], monkeypatch)

        def detect(computed_fun):
            return DetectorYield(detector, computed_fun)

        yield detect
