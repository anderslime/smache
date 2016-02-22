from mongoengine import signals
from smache.smache_logging import logger

class MongoDataSource:
    def __init__(self, document):
        self.document = document
        self.data_source_id = document.__name__
        self._subscriber = lambda x: x

    def subscribe(self, fun):
        logger.debug("{} subscribed to {}".format(fun.__name__, self.data_source_id))
        self._subscriber = fun
        signals.post_save.connect(
            self._mongoengine_post_save,
            sender=self.document
        )

    def serialize(self, entity):
        return str(entity.id)

    def find(self, entity_id):
        return self.document.objects(id=entity_id).first()

    def _mongoengine_post_save(self, sender, document, **kwargs):
        logger.debug("{} updated - notifying subscriber {}".format(document, self._subscriber.__name__))
        self._subscriber(self, document.id)
