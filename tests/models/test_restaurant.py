from random import random

from app.models.restaurant import Restaurant
import uuid


def insert_restaurants(n, db_session):
    for i in range(0, n):
        db_session.add(Restaurant(name=f"Test Restaurant #{i}", cuisine="French", place_id=str(uuid.uuid4()),
                                  place_lat=float(random()), place_long=float(random())))
    db_session.commit()


class TestRestaurantModel:
    def test_saves_restaurants(self, db_session):
        insert_restaurants(10, db_session)

    def test_query_restaurants(self, db_session):
        insert_restaurants(10, db_session)
        restaurants = db_session.query(Restaurant).all()
        assert len(restaurants) == 10
