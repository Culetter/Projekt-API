import pytest
from sqlalchemy import create_mock_engine, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from database import Base, get_db
from main import app
from fastapi.testclient import TestClient
from services.auth_service import get_current_user

# Використовуємо SQLite в пам'яті для тестів
SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Створюємо таблиці в тестовій БД
Base.metadata.create_all(bind=engine)

@pytest.fixture
def session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def test_user():
    # Мокаємо користувача, щоб не тестувати логіку JWT тут
    return {"username": "testuser", "role": "admin", "id": 1}

@pytest.fixture
def authorized_client(client, test_user):
    # Перевизначаємо залежність авторизації
    app.dependency_overrides[get_current_user] = lambda: test_user
    return client