import os
import sys
import mongomock
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import app


@pytest.fixture
def client():
    # use a fake MongoDB so tests run without a real database
    app.config["TESTING"] = True
    app.mongo_client = mongomock.MongoClient()
    with app.test_client() as client:
        yield client
    del app.mongo_client


def add_sample(client):
    res = client.post("/products", json={"name": "Laptop", "price": 999.99, "stock": 5})
    return res.get_json()["id"]


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


def test_add_product(client):
    res = client.post("/products", json={"name": "Mouse", "price": 25, "stock": 10})
    assert res.status_code == 201
    body = res.get_json()
    assert body["name"] == "Mouse"
    assert "id" in body


def test_add_product_missing_name(client):
    res = client.post("/products", json={"price": 10})
    assert res.status_code == 400


def test_add_product_bad_price(client):
    res = client.post("/products", json={"name": "Pen", "price": -5})
    assert res.status_code == 400


def test_list_products(client):
    add_sample(client)
    add_sample(client)
    res = client.get("/products")
    assert res.status_code == 200
    assert len(res.get_json()) == 2


def test_get_product(client):
    product_id = add_sample(client)
    res = client.get(f"/products/{product_id}")
    assert res.status_code == 200
    assert res.get_json()["name"] == "Laptop"


def test_get_product_not_found(client):
    res = client.get("/products/abc123")
    assert res.status_code == 404


def test_update_product(client):
    product_id = add_sample(client)
    res = client.put(f"/products/{product_id}", json={"price": 899.99})
    assert res.status_code == 200
    assert res.get_json()["price"] == 899.99


def test_delete_product(client):
    product_id = add_sample(client)
    res = client.delete(f"/products/{product_id}")
    assert res.status_code == 200
    assert client.get(f"/products/{product_id}").status_code == 404


def test_metrics(client):
    res = client.get("/metrics")
    assert res.status_code == 200
