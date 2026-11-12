# ShopLite – Microservices Project

Team: Maha Al-Tuhfi, Saheedat Abbas, Victor Varon

| Service | Owner | Port | Database |
|---|---|---|---|
| user-service | Maha | 5001 | PostgreSQL |
| product-service | Saheedat | 5002 | MongoDB |
| order-service | Victor | 5003 | PostgreSQL |

## Run locally with Docker Compose

```bash
cp .env.example .env      # then edit the passwords
docker compose up --build
```

## User Service API

| Method | Endpoint | Body | Returns |
|---|---|---|---|
| POST | /users | `{"name","email","password"}` | 201 + user |
| POST | /login | `{"email","password"}` | 200 + token |
| GET | /users/{id} | – | 200 + user / 404 |
| GET | /health | – | 200 |
| GET | /metrics | – | Prometheus metrics |

## Run the User Service tests

```bash
cd user-service
pip install -r requirements-dev.txt
pytest -v
```