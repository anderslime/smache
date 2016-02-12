from mongoengine import signals

class MongoDataSource:
    def __init__(self, document):
        self.document = document
        self.subscriber = lambda x: x
        self.subscribes_to_mongoengine = False
        self.data_source_id = document.__name__

    def subscribe(self, fun):
        self.subscriber = fun
        if not self.subscribes_to_mongoengine:
            signals.post_save.connect(
                self._mongoengine_post_save,
                sender=self.document
            )

    def serialize(self, entity):
        return str(entity.id)

    def find(self, entity_id):
        return self.document.objects(id=entity_id)

    def did_update(self, entity_id):
        self.subscriber(self, entity_id)

    def _mongoengine_post_save(self, sender, document, **kwargs):
        self.did_update(document.id)
