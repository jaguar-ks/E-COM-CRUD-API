# E-COM CRUD API

A FastAPI + SQLModel ecommerce CRUD API with modular routes, Swagger docs, pagination, and business rules for stock and order totals.

## Navigation

- [Quick run & test](#quick-run--test)
- [Documentation URLs](#documentation-urls)
- [Technologies Used](#technologies-used)
- [Project File Organization](#project-file-organization)
- [Testing](#testing)
- [API & Tooling](#api--tooling)
- [Database UML Demo](#database-uml-demo)
- [Model Reference](#model-reference)
- [API Endpoint Reference](#api-endpoint-reference)

## Quick run & test

The repository is designed to be driven through the `Makefile`. Start with `make help` to see the available targets and then follow the workflow below.

### 0. Clone the repository

If you have not cloned the project yet, get the source and enter the folder first:

```bash
git clone git@github.com:jaguar-ks/E-COM-CRUD-API.git
cd E-COM-CRUD-API
```

```bash
make help
```

### 1. Create the environment and install dependencies

```bash
make venv
make install
```

### 2. Start the API

Run the API in a terminal while developing:

```bash
make run-api
```

For auto-reload during development:

```bash
make run-api-dev
```

### 3. Seed the database

Populate the SQLite database with the deterministic CSV fixtures used by the app and tests:

```bash
make seed
```

The seeder reads from [data/test](data/test) and is also triggered automatically when `main.py` starts and the database is empty.

### 4. Run Robot Framework E2E tests

Run the Robot suites against a running API:

```bash
make test-robot
```

Validate suite structure and CSV parsing without sending HTTP requests:

```bash
make test-robot-dry
```

Run the suites locally with the API started and stopped for you:

```bash
make test-robot-local
```

Run the suites in parallel with `pabot` using test-level split:

```bash
make test-pabot
```

### 5. Maintain or reset the workspace

Check the API health endpoint before running tests:

```bash
make check-api
```

Remove Robot output files:

```bash
make clean-results
```

Reset the local SQLite database file:

```bash
make reset-db
```

Run the Python syntax check and general cleanup:

```bash
make lint
make clean
```

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
        - [utils/db.py](utils/db.py)
        - [utils/seed_database.py](utils/seed_database.py)
    - [data/](data) — CSV fixtures and seeds
        - [data/test/](data/test) — deterministic seed CSVs used by `utils/seed_database.py`
    - [tests/](tests) — test documentation and Robot suites
        - [tests/README.md](tests/README.md) — consolidated Robot docs
        - [tests/robot/](tests/robot) — Robot suites, resources, and data
    - [Makefile](Makefile) — convenience targets (venv, install, run, test, seed)
    - [req.txt](req.txt) — pinned Python deps (includes Robot + pabot)
    - [.gitignore](.gitignore) — ignores robot results and local artifacts
    - [README.md](README.md)

## API Endpoint Reference

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
