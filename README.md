# E-COM CRUD API

A FastAPI + SQLModel ecommerce CRUD API with modular routes, Swagger docs, pagination, and business rules for stock and order totals.

## Navigation

- [Installation and Running Guide](#installation-and-running-guide)
- [Documentation URLs](#documentation-urls)
- [Technologies Used](#technologies-used)
- [Project File Organization](#project-file-organization)
- [Quick Start (install, run, test)](#quick-start-install-run-test)
- [Testing](#testing)
- [API & Tooling](#api--tooling)
- [Database UML Demo](#database-uml-demo)
- [Model Reference](#model-reference)
- [API Endpoint Reference](#api-endpoint-reference)
- [Business Rules Implemented](#business-rules-implemented)
- [Common Status Codes](#common-status-codes)

## Installation and Running Guide

### 1. Clone and open the project

```bash
git clone git@github.com:jaguar-ks/E-COM-CRUD-API.git
cd E-COM-CRUD-API
```

### 2. Create and activate virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r req.txt
```

### 4. Run the API

```bash
uvicorn main:app --reload
```

### 5. Open API docs

- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### 6. Seed demo data

Run the seed script to populate the local SQLite database with sample categories, customers, products, orders, and order items:

```bash
python -m utils.seed_database
```

The script clears existing rows first so the demo data stays reproducible.
The mock rows are stored as CSV fixtures under [data/test](data/test).

## 7. Run Robot Framework E2E (DDT)

The project includes Robot Framework DataDriver suites under `tests/robot/` driven by semicolon-delimited CSV fixtures.

Install project dependencies (recommended via the Makefile):

```bash
make venv
make install
```

Start the API (separate terminal):

```bash
make run-api
```

Run Robot suites (requires API running):

```bash
make test-robot
```

Run Robot suites locally (start API, run tests, stop API):

```bash
make test-robot-local
```

Run Robot suites in parallel with `pabot` (test-level split):

```bash
make test-pabot
```

Robot test project files are under `tests/robot` and CSV fixtures for seeding are in `data/test`.

## Documentation URLs

| Name | URL |
|---|---|
| Base API | [http://127.0.0.1:8000](http://127.0.0.1:8000) |
| Health Check | [http://127.0.0.1:8000/](http://127.0.0.1:8000/) |
| Swagger UI | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) |
| ReDoc | [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) |

## Project File Organization

- [E-COM-CRUD-API](.)
    - [main.py](main.py)
    - [db.py](db.py)
    - [models/](models) — SQLModel models and Pydantic schemas
        - [models/__init__.py](models/__init__.py)
        - [models/product.py](models/product.py)
        - [models/category.py](models/category.py)
        - [models/customer.py](models/customer.py)
        - [models/order.py](models/order.py)
        - [models/order_item.py](models/order_item.py)
    - [routes/](routes) — FastAPI route modules
        - [routes/__init__.py](routes/__init__.py)
        - [routes/products.py](routes/products.py)
        - [routes/categories.py](routes/categories.py)
        - [routes/customers.py](routes/customers.py)
        - [routes/orders.py](routes/orders.py)
        - [routes/order_items.py](routes/order_items.py)
    - [utils/](utils) — helper scripts (seeder, misc)
        - [utils/seed_database.py](utils/seed_database.py)
    - [data/](data) — CSV fixtures and seeds
        - [data/test/](data/test) — deterministic seed CSVs used by `utils/seed_database.py`
    - [tests/](tests) — test documentation and Robot suites
        - [tests/README.md](tests/README.md) — consolidated Robot docs
        - [tests/robot/](tests/robot) — Robot suites, resources, data, and results
    - [Makefile](Makefile) — convenience targets (venv, install, run, test, seed)
    - [req.txt](req.txt) — pinned Python deps (includes Robot + pabot)
    - [.gitignore](.gitignore) — ignores robot results and local artifacts
    - [README.md](README.md)
    - [database.db](database.db)

## Database UML Demo

Graphical ER/UML demo (Mermaid):

```mermaid
erDiagram
    CATEGORY {
        int id PK
        string name "UNIQUE"
        string description
    }

    PRODUCT {
        int id PK
        string name
        string description
        int price
        int stock_quantity
        int category_id FK
        datetime created_at
    }

    CUSTOMER {
        int id PK
        string first_name
        string last_name
        string email "UNIQUE"
        string phone
        datetime created_at
    }

    ORDER {
        int id PK
        int customer_id FK
        datetime order_date
        int total_amount
        string status
    }

    ORDER_ITEM {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
        int price
    }

    CATEGORY ||--o{ PRODUCT : contains
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--o{ ORDER_ITEM : has
    PRODUCT ||--o{ ORDER_ITEM : appears_in
```

## Model Reference

| Model | File | Kind | Main Fields | Relationships | Used By Endpoints |
|---|---|---|---|---|---|
| ProductCreate | [models/product.py](models/product.py) | Request schema | name, description, price, stock_quantity, category_id | category_id -> Category | POST/PUT products |
| Product | [models/product.py](models/product.py) | Response + table | id, created_at + ProductCreate fields | belongs to Category, has many OrderItem | All products endpoints |
| CategoryCreate | [models/category.py](models/category.py) | Request schema | name, description | None | POST/PUT categories |
| Category | [models/category.py](models/category.py) | Response + table | id + CategoryCreate fields | has many Product | All categories endpoints |
| CustomerCreate | [models/customer.py](models/customer.py) | Request schema | first_name, last_name, email, phone | None | POST/PUT customers |
| Customer | [models/customer.py](models/customer.py) | Response + table | id, created_at + CustomerCreate fields | has many Order | All customers endpoints |
| OrderCreate | [models/order.py](models/order.py) | Request schema | customer_id, order_date, total_amount, status | customer_id -> Customer | POST/PUT orders |
| Order | [models/order.py](models/order.py) | Response + table | id + OrderCreate fields | belongs to Customer, has many OrderItem | All orders endpoints |
| OrderItemCreate | [models/order_item.py](models/order_item.py) | Request schema | order_id, product_id, quantity, price | order_id -> Order, product_id -> Product | POST/PUT order-items |
| OrderItem | [models/order_item.py](models/order_item.py) | Response + table | id + OrderItemCreate fields | belongs to Order and Product | All order-items endpoints |
| OrderStatus | [models/order.py](models/order.py) | Enum | Pending, Completed, Cancelled | Used by Order.status | Orders endpoints |

## API Endpoint Reference

Base URL: [http://127.0.0.1:8000](http://127.0.0.1:8000)

### Products Endpoints

| Method | Endpoint URL | Request Model | Response Model | Notes |
|---|---|---|---|---|
| POST | [http://127.0.0.1:8000/products](http://127.0.0.1:8000/products) | ProductCreate | Product | Create product |
| GET | [http://127.0.0.1:8000/products](http://127.0.0.1:8000/products) | None | list of Product | Supports skip and limit |
| GET | [http://127.0.0.1:8000/products/{product_id}](http://127.0.0.1:8000/products/%7Bproduct_id%7D) | None | Product | Get one product |
| PUT | [http://127.0.0.1:8000/products/{product_id}](http://127.0.0.1:8000/products/%7Bproduct_id%7D) | ProductCreate | Product | Update product |
| DELETE | [http://127.0.0.1:8000/products/{product_id}](http://127.0.0.1:8000/products/%7Bproduct_id%7D) | None | 204 No Content | Delete product |

### Categories Endpoints

| Method | Endpoint URL | Request Model | Response Model | Notes |
|---|---|---|---|---|
| POST | [http://127.0.0.1:8000/categories](http://127.0.0.1:8000/categories) | CategoryCreate | Category | Create category |
| GET | [http://127.0.0.1:8000/categories](http://127.0.0.1:8000/categories) | None | list of Category | Supports skip and limit |
| GET | [http://127.0.0.1:8000/categories/{category_id}](http://127.0.0.1:8000/categories/%7Bcategory_id%7D) | None | Category | Get one category |
| PUT | [http://127.0.0.1:8000/categories/{category_id}](http://127.0.0.1:8000/categories/%7Bcategory_id%7D) | CategoryCreate | Category | Update category |
| DELETE | [http://127.0.0.1:8000/categories/{category_id}](http://127.0.0.1:8000/categories/%7Bcategory_id%7D) | None | 204 No Content | Delete category |

### Customers Endpoints

| Method | Endpoint URL | Request Model | Response Model | Notes |
|---|---|---|---|---|
| POST | [http://127.0.0.1:8000/customers](http://127.0.0.1:8000/customers) | CustomerCreate | Customer | Create customer |
| GET | [http://127.0.0.1:8000/customers](http://127.0.0.1:8000/customers) | None | list of Customer | Supports skip and limit |
| GET | [http://127.0.0.1:8000/customers/{customer_id}](http://127.0.0.1:8000/customers/%7Bcustomer_id%7D) | None | Customer | Get one customer |
| PUT | [http://127.0.0.1:8000/customers/{customer_id}](http://127.0.0.1:8000/customers/%7Bcustomer_id%7D) | CustomerCreate | Customer | Update customer |
| DELETE | [http://127.0.0.1:8000/customers/{customer_id}](http://127.0.0.1:8000/customers/%7Bcustomer_id%7D) | None | 204 No Content | Delete customer |

### Orders Endpoints

| Method | Endpoint URL | Request Model | Response Model | Notes |
|---|---|---|---|---|
| POST | [http://127.0.0.1:8000/orders](http://127.0.0.1:8000/orders) | OrderCreate | Order | Create order |
| GET | [http://127.0.0.1:8000/orders](http://127.0.0.1:8000/orders) | None | list of Order | Supports skip and limit |
| GET | [http://127.0.0.1:8000/orders/{order_id}](http://127.0.0.1:8000/orders/%7Border_id%7D) | None | Order | Get one order |
| PUT | [http://127.0.0.1:8000/orders/{order_id}](http://127.0.0.1:8000/orders/%7Border_id%7D) | OrderCreate | Order | Update order |
| DELETE | [http://127.0.0.1:8000/orders/{order_id}](http://127.0.0.1:8000/orders/%7Border_id%7D) | None | 204 No Content | Delete order |

### Order Items Endpoints

| Method | Endpoint URL | Request Model | Response Model | Notes |
|---|---|---|---|---|
| POST | [http://127.0.0.1:8000/order-items](http://127.0.0.1:8000/order-items) | OrderItemCreate | OrderItem | Creates item and decreases stock |
| GET | [http://127.0.0.1:8000/order-items](http://127.0.0.1:8000/order-items) | None | list of OrderItem | Supports skip and limit |
| GET | [http://127.0.0.1:8000/order-items/{order_item_id}](http://127.0.0.1:8000/order-items/%7Border_item_id%7D) | None | OrderItem | Get one order item |
| PUT | [http://127.0.0.1:8000/order-items/{order_item_id}](http://127.0.0.1:8000/order-items/%7Border_item_id%7D) | OrderItemCreate | OrderItem | Reconciles stock and totals |
| DELETE | [http://127.0.0.1:8000/order-items/{order_item_id}](http://127.0.0.1:8000/order-items/%7Border_item_id%7D) | None | 204 No Content | Restores stock and recalculates total |

## Technologies Used
| Technology | Icon | Version | Purpose |
|---|---|---|---|
| Python | ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white) | 3.x | Core programming language |
| FastAPI | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white) | 0.135.2 | Web framework and OpenAPI generation |
| SQLModel | ![SQLModel](https://img.shields.io/badge/SQLModel-0F172A?logo=databricks&logoColor=white) | 0.0.37 | ORM models and schema integration |
| SQLAlchemy | ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?logo=sqlite&logoColor=white) | 2.0.48 | Database ORM engine |
| Pydantic | ![Pydantic](https://img.shields.io/badge/Pydantic-E92063?logo=pydantic&logoColor=white) | 2.12.5 | Data validation and serialization |
| Uvicorn | ![Uvicorn](https://img.shields.io/badge/Uvicorn-222222?logo=gunicorn&logoColor=white) | 0.42.0 | ASGI server for running the API |
| Robot Framework | ![Robot](https://img.shields.io/badge/RobotFramework-000000?logo=robotframework&logoColor=white) | 7.3.2 | E2E test runner and DSL |
| robotframework-requests | ![Requests](https://img.shields.io/badge/Requests-000000) | 0.9.7 | HTTP wrapper for REST calls |
| robotframework-datadriver | ![DataDriver](https://img.shields.io/badge/DataDriver-000000) | 1.11.2 | CSV-driven Data-Driven Testing (DDT) |
| pabot | ![pabot](https://img.shields.io/badge/pabot-000000) | (installed via `req.txt`) | Parallel execution runner for Robot |
| SQLite | ![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white) | File-based DB | Local development database |

## Testing

- Consolidated Robot documentation into `tests/README.md` (suite overviews, keywords reference, and scenario descriptions).
- Added extra DataDriver rows to `tests/robot/data/*` to expand DDT coverage (3 cases per suite).
- Added a `pabot`-based parallel run target to the `Makefile`: `make test-pabot` (uses `--testlevelsplit`). Ensure `pabot` is installed (`req.txt` updated).
- `.gitignore` updated to ignore Robot run artifacts (`tests/robot/results/`, `output.xml`, `log.html`, `report.html`).

See [tests/README.md](tests/README.md) for full Robot/DATADRIVER documentation and run examples.

## API & Tooling

- `main.py` now checks the database on startup and will run the deterministic seeder when the DB is empty. This makes local runs reproducible and helpful for CI.
- Deterministic seeding code is implemented in [utils/seed_database.py](utils/seed_database.py). It reads CSV fixtures from [data/test](data/test) and populates `categories`, `customers`, `products`, `orders`, and `order_items`.
- `Makefile` was extended with convenient targets: `venv`, `install`, `run-api`, `run-api-dev`, `seed`, `check-api`, `test-robot`, `test-robot-local`, `test-robot-dry`, and `test-pabot` (parallel runs via `pabot --testlevelsplit`). Use `make seed` to run the seeder manually.
- `req.txt` now includes `pabot` so `make install` will provide the tool used for parallel Robot runs.

## Quick command summary

Use the Makefile targets for common flows (recommended):

```bash
# create venv and install deps
make venv
make install

# seed DB (optional — app will seed on startup if DB is empty)
make seed

# run API
make run-api

# run Robot suites (requires API running)
make test-robot

# run Robot suites in parallel (pabot, test-level split)
make test-pabot

# start API, run Robot suites, then stop API
make test-robot-local
```

## Files of interest

- Seeder & fixtures: [utils/seed_database.py](utils/seed_database.py) and [data/test](data/test)
- Robot tests & DDT fixtures: [tests/robot](tests/robot) and main test doc [tests/README.md](tests/README.md)
- Makefile: [Makefile](Makefile) — convenient targets as shown above
- Requirements: [req.txt](req.txt) — includes `pabot` and Robot deps
- Ignored artifacts: `.gitignore` updated to ignore Robot result files in `tests/robot/results/`.
