# Product Service (Saheedat)

Flask REST API for ShopLite products. Uses MongoDB. Runs on port 5002.

## Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /products | Add a product (name and price required) |
| GET | /products | List all products |
| GET | /products/{id} | Get one product |
| PUT | /products/{id} | Update one product |
| DELETE | /products/{id} | Delete one product |
| GET | /health | Health check |
| GET | /metrics | Prometheus metrics |

## Environment variables

MONGO_HOST (default localhost), MONGO_PORT (27017), MONGO_DB (productdb), MONGO_USER, MONGO_PASSWORD, PORT (5002)

## Run tests (no database needed)

pip install -r requirements.txt
python -m pytest -v

## Run with Docker

docker build -t product-service:1.0 .
