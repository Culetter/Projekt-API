from starlette import status

def test_create_product(authorized_client):
    response = authorized_client.post(
        "/products/",
        json={"product_name": "Laptop", "price": 999.99}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["product_name"] == "Laptop"
    assert "id" in data

def test_read_product(authorized_client, session):
    # Спочатку створимо продукт вручну через сервіс або прямо в БД
    from models import Product # Імпортуйте вашу модель
    new_product = Product(product_name="Phone", price=500.0)
    session.add(new_product)
    session.commit()

    response = authorized_client.get(f"/products/{new_product.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["product_name"] == "Phone"

def test_update_product(authorized_client, session):
    from models import Product
    product = Product(product_name="Old Name", price=10.0)
    session.add(product)
    session.commit()

    response = authorized_client.put(
        f"/products/update/{product.id}",
        json={"product_name": "New Name", "price": 20.0}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["product_name"] == "New Name"

def test_delete_product(authorized_client, session):
    from models import Product
    product = Product(product_name="To Delete", price=1.0)
    session.add(product)
    session.commit()

    response = authorized_client.delete(f"/products/delete/{product.id}")
    assert response.status_code == status.HTTP_200_OK
    
    # Перевіряємо, чи видалено з БД
    deleted_product = session.query(Product).filter(Product.id == product.id).first()
    assert deleted_product is None

def test_create_product_unauthorized(client):
    # Використовуємо звичайний client БЕЗ авторизації
    response = client.post(
        "/products/",
        json={"product_name": "Hack", "price": 0.01}
    )
    # Має бути 401, бо get_current_user не спрацює без токена
    assert response.status_code == status.HTTP_401_UNAUTHORIZED