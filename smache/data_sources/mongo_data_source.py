from mongoengine import signals, Document
from ..smache_logging import logger


class MongoDataSource:

    @classmethod
    def data_source_id(cls, document):
        return document.__name__

    @classmethod
    def is_instance(cls, document_class):
        return issubclass(document_class, Document)

    def __init__(self, document):
        self.document = document
        self.data_source_id = self.__class__.data_source_id(document)
        self._subscriber = lambda x: x

    def subscribe(self, fun):
        logger.debug(
            "{} subscribed to {}".format(fun.__name__, self.data_source_id)
        )
        self._subscriber = fun
        signals.post_save.connect(
            self._mongoengine_post_save,
            sender=self.document
        )
        signals.post_delete.connect(
            self._mongoengine_post_save,
            sender=self.document
        )
        signals.post_bulk_insert.connect(
            self._mongoengine_post_saves,
            sender=self.document
        )

    def for_entity(self, document_instance):
        return self.data_source_id == document_instance.__class__.__name__

    def for_entity_class(self, document):
        return self.data_source_id == self.__class__.data_source_id(document)

    def serialize(self, entity):
        return str(entity.id)

    def find(self, entity_id):
        return self.document.objects(id=entity_id).first()

    def disconnect(self):
        signals.post_save.disconnect(self._mongoengine_post_save)
        signals.post_delete.disconnect(self._mongoengine_post_save)
        signals.post_bulk_insert.disconnect(self._mongoengine_post_saves)

    def _mongoengine_post_saves(self, sender, documents, **kwargs):
        for document in self._loaded_documents(documents, **kwargs):
            self._mongoengine_post_save(sender, document, **kwargs)

    def _loaded_documents(self, documents, **kwargs):
        if kwargs.pop('loaded', True):
            return documents
        else:
            logger.warn(
                "Smache: document updates are not received when using "
                "bulk insert without load"
            )
            return []

    def _mongoengine_post_save(self, sender, document, **kwargs):
        self._log_notification(document)
        self._subscriber(self, document)

    def _log_notification(self, document):
        message = "{}({}) updated - notifying subscriber {}".format(
            document,
            str(document.id),
            self._subscriber.__name__
        )
        logger.debug(message)
