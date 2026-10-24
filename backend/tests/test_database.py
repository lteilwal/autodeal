from sqlalchemy import text


def test_db_session_uses_test_database(db_session):
    result = db_session.execute(text("SELECT current_database()")).scalar()

    assert result == "car_inventory_test"
