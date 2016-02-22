from mongoengine import Document, StringField, IntField, connect

db = connect('testdb', host='localhost', port=27017,)

class User(Document):
    name = StringField()
    age = IntField()
