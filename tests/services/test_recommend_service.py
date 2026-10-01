from datetime import date

from app.models import Restaurant, User, Visit
from app.services import recommend


def add_visits(db, tiers):
    user = User()
    db.add(user)
    db.commit()
    for i, tier in enumerate(tiers):
        r = Restaurant(name=f"R{i}", cuisine=["thai"], price_tier=tier, place_id=str(i), place_lat=0.0, place_long=0.0)
        db.add(r)
        db.commit()
        db.add(Visit(user_id=user.id, restaurant_id=r.id, date=date.today()))
    db.commit()
    return user.id


def test_unspecified_prices_are_ignored(db_session):
    user_id = add_visits(db_session, [-1, -1, 2, 2, 3])
    prefs = recommend.get_user_preferences(db_session, user_id)
    assert prefs.price_tier == 2


def test_median_is_an_int(db_session):
    user_id = add_visits(db_session, [1, 2, 2, 3, 3, 3])
    prefs = recommend.get_user_preferences(db_session, user_id)
    assert isinstance(prefs.price_tier, int)


def test_all_prices_unspecified(db_session):
    user_id = add_visits(db_session, [-1] * 5)
    prefs = recommend.get_user_preferences(db_session, user_id)
    assert prefs.price_tier == -1
