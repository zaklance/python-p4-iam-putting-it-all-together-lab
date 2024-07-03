from flask import Flask
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import MetaData

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    recipes = db.relationship('Recipe', back_populates='users')

    @hybrid_property
    def password_hash(self): 
        if self is True: 
            return self._password_hash
        else:
            raise AttributeError(f'login is incorrect')

    @password_hash.setter
    def password_hash(self, new_password):
        password_hash = bcrypt.generate_password_hash(new_password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password): 
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))
    
    serialize_rules = ['-recipes.users', '-_password_hash']

    def __repr__(self):
        return f"<User {self.username}>"

class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    users = db.relationship('User', back_populates='recipes')
    
    @validates('instructions')
    def validate_instructions(self, key, new_value):
        if len(new_value) < 50: 
            raise ValueError(f'{key} cannot be less than 50 characters')
        return new_value