from mongoengine import Document, StringField, IntField, connect, ListField, ReferenceField


def test_connect():
    connect('testdb', host='localhost', port=27017,)


class User(Document):
    name = StringField()
    age = IntField()


class Handin(Document):
    users = ListField(ReferenceField(User))
    score = IntField()
