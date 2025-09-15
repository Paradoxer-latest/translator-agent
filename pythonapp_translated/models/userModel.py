from mongoengine import Document, StringField, EmailField


class User(Document):
    username = StringField(required=True)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)

    meta = {"collection": "users"}
