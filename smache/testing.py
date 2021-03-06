import sys
import smache
from pymongo.cursor import Cursor
from smache.data_sources import MongoDataSource


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
            msg = "The smache computed function '{}' is using data from the " \
                "sources '{}' without subscribing to it/them".format(
                    self.computed_fun.__name__,
                    self.detector.collection_diff_names()
                )
            raise RelationMissingError(msg)
        else:
            self.detector.cleanup()


class RelationDetector:
    def __init__(self, documents):
        self.documents = documents
        self.detected_collections = set()

    def mark_as_detected(self, collection):
        if collection.name not in self._detected_collection_names():
            self.detected_collections.add(collection)

    def has_anything_to_report(self):
        collection_diff = self.collection_diff_names()
        return len(collection_diff) > 0

    def print_report(self):
        if self.has_anything_to_report():
            self._print_report_in_console()

    def _print_report_in_console(self):
        computed_fun = smache._instance._computed_repo.get(self.computed_fun)
        print "WARNING: The computed function {} used data from the " \
            "collections '{}' without subscribing to it".format(
                computed_fun.fun.__name__,
                self.collection_diff_names()
            )

    def _collection_diff(self):
        computed_fun = smache._instance._computed_repo.get(self.computed_fun)
        collections = self._collections(computed_fun.arg_deps) \
            + self._collections(computed_fun.data_source_deps) \
            + self._collections([ds for ds, _ in computed_fun.relation_deps])
        detected_collection_names = set(self._detected_collection_names())
        subscribed_collection_names = set([col.name for col in collections])
        return detected_collection_names - subscribed_collection_names

    def collection_diff_names(self):
        return ', '.join(self._collection_diff())

    def _collections(self, data_sources):
        return [data_source.document._get_collection()
                for data_source in self._mongo_data_sources(data_sources)]

    def _mongo_data_sources(self, data_sources):
        return [data_source for data_source in data_sources
                if self._is_mongo_data_source(data_source)]

    def _is_mongo_data_source(self, data_source):
        return hasattr(data_source, 'document') and \
            MongoDataSource.is_instance(data_source.document)

    def _detected_collection_names(self):
        return [col.name for col in self.detected_collections]

    def start_detecting(this_detector, computed_fun):
        this_detector.computed_fun = computed_fun
        old_init = Cursor.__init__
        this_detector._old_cursor_init = old_init

        def new_init(cursor_self, *args, **kwargs):
            collection = args[0]
            this_detector.mark_as_detected(collection)
            return old_init(cursor_self, *args, **kwargs)

        setattr(Cursor, '__init__', new_init)

    def cleanup(this_detector):
        setattr(Cursor, '__init__', this_detector._old_cursor_init)


if 'pytest' in sys.modules:
    import pytest

    @pytest.yield_fixture(scope="class")
    def relation_detector():
        detector = RelationDetector([])

        def detect(computed_fun):
            return DetectorYield(detector, computed_fun)

        yield detect


def detect_dependencies_for(computed_fun):
    detector = RelationDetector([])
    return DetectorYield(detector, computed_fun)
