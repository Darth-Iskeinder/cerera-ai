import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Создание объекта-сессии
engine = sqlalchemy.create_engine('postgresql://postgres:123456@localhost/postgres')
Session = sessionmaker(bind=engine)
session = Session()

# Создание базового класса модели
Base = declarative_base()

class Destination(Base):
    __tablename__ = 'destinations'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    value = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    key = sqlalchemy.Column(sqlalchemy.String, nullable=False)

def get_all_destinations():
    return session.query(Destination).all()

class Origin(Base):
    __tablename__ = 'origins'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    value = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    key = sqlalchemy.Column(sqlalchemy.String, nullable=False)

def get_all_origins():
    return session.query(Origin).all()

class Product(Base):
    __tablename__ = 'products'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    value = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    key = sqlalchemy.Column(sqlalchemy.String, nullable=False)

def get_all_products():
    return session.query(Product).all()