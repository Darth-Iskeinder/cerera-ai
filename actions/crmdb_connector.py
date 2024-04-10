import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, func
from datetime import datetime, timedelta

# Создание объекта-сессии
engine = sqlalchemy.create_engine('postgresql://postgres:123456@localhost/back')
Session = sessionmaker(bind=engine)
session = Session()

# Создание базового класса модели
Base = declarative_base()


class Products(Base):
    __tablename__ = '1_products'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    tour_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    duration = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    start_date = sqlalchemy.Column(sqlalchemy.TIMESTAMP, nullable=False)
    end_date = sqlalchemy.Column(sqlalchemy.TIMESTAMP, nullable=False)
    tour_type = sqlalchemy.Column(sqlalchemy.TIMESTAMP, nullable=False)
    country = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    departure_city = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    arrival_city = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    tour_status = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    available_seats = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    currency = sqlalchemy.Column(sqlalchemy.String, nullable=False)


def get_filtered_products(**filters):
    query = session.query(Products)

    if filters:
        filter_conditions = []
        for column, value in filters.items():
            if hasattr(Products, column) and value:
                column_type = getattr(Products, column).type
                if isinstance(column_type, datetime) or column_type.__class__.__name__ == 'TIMESTAMP':
                    if not isinstance(value, datetime) and not isinstance(value, list):
                        value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                    if isinstance(value, datetime):
                        filter_conditions.append(getattr(Products, column) == value)
                    elif isinstance(value, list):
                        if len(value) == 1:
                            value[0] = datetime.strptime(value[0], '%Y-%m-%dT%H:%M:%S.%f%z')
                            start_date = value[0] - timedelta(days=10)
                            end_date = value[0] + timedelta(days=10)

                            filter_conditions.append(getattr(Products, column).between(start_date, end_date))
                        elif len(value) == 2:
                            filter_conditions.append(getattr(Products, column).between(*value))
                elif column_type.__class__.__name__ == 'String':
                    filter_conditions.append(func.levenshtein(getattr(Products, column), value) <= 3)
                else:
                    filter_conditions.append(getattr(Products, column) == value)

        if filter_conditions:
            query = query.filter(and_(*filter_conditions))
    return query.all()
