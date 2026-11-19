import pytest

from src.main.api.db.engine import SessionLocal, engine


@pytest.fixture(scope='function')
def db_session():
    """Создаёт изолированную сессию БД на время теста с откатом транзакции после завершения."""
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
