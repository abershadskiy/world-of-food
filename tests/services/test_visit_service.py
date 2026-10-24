from datetime import date

import pytest
from fastapi import HTTPException

from app.dto.visit import VisitUpdate
from app.models import Visit
from app.services import visit as visit_service
from tests.factories import make_restaurant, make_user


@pytest.fixture
def saved_visit(db_session):
    user = make_user()
    restaurant = make_restaurant()
    db_session.add_all([user, restaurant])
    db_session.commit()
    visit = Visit(user_id=user.id, restaurant_id=restaurant.id, date=date(2026, 1, 1), rating=3, notes="ok")
    db_session.add(visit)
    db_session.commit()
    return visit


class TestUpdateVisit:
    def test_changes_only_the_fields_sent(self, db_session, saved_visit):
        changes = VisitUpdate.model_validate({"rating": 5})

        updated = visit_service.update_visit(db_session, saved_visit.user_id, saved_visit.id, changes)

        assert updated.rating == 5
        assert updated.notes == "ok"
        assert updated.date == date(2026, 1, 1)

    def test_null_clears_a_field(self, db_session, saved_visit):
        changes = VisitUpdate.model_validate({"notes": None})

        updated = visit_service.update_visit(db_session, saved_visit.user_id, saved_visit.id, changes)

        assert updated.notes is None

    def test_other_users_visit_is_404(self, db_session, saved_visit):
        with pytest.raises(HTTPException) as error:
            visit_service.update_visit(db_session, saved_visit.user_id + 1, saved_visit.id, VisitUpdate(rating=1))

        assert error.value.status_code == 404
        db_session.refresh(saved_visit)
        assert saved_visit.rating == 3


class TestDeleteVisit:
    def test_removes_the_visit(self, db_session, saved_visit):
        visit_service.delete_visit(db_session, saved_visit.user_id, saved_visit.id)

        assert visit_service.get_visits(db_session, saved_visit.user_id) == []

    def test_other_users_visit_is_404(self, db_session, saved_visit):
        with pytest.raises(HTTPException) as error:
            visit_service.delete_visit(db_session, saved_visit.user_id + 1, saved_visit.id)

        assert error.value.status_code == 404
        assert len(visit_service.get_visits(db_session, saved_visit.user_id)) == 1
