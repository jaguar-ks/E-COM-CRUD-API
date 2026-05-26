# E-COM CRUD API — Tests documentation

This document centralizes test tooling, data, workflows, and human-readable scenarios used for end-to-end verification of the API.

## Navigation

- [Documentation URLs](#documentation-urls)
- [Technologies Used](#technologies-used)
- [Project File Organization](#project-file-organization)
- [Quick Start (install, run, test)](#quick-start-install-run-test)
- [Test Suite Overview](#test-suite-overview)
- [Troubleshooting](#troubleshooting)
- [Suite overviews](#suite-overviews)
- [Keywords reference](#keywords-reference)
- [Scenarios](#scenarios)

## Documentation URLs

| Name | URL |
|---|---|
| Base API | [http://127.0.0.1:8000](http://127.0.0.1:8000) |
| Health Check | [http://127.0.0.1:8000/](http://127.0.0.1:8000/) |
| Swagger UI | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) |
| ReDoc | [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) |

## Technologies Used

| Technology | Icon | Purpose |
|---|---|---|
| Robot Framework | ![Robot](https://img.shields.io/badge/RobotFramework-000000?logo=robotframework&logoColor=white) | E2E test runner and DSL |
| robotframework-requests | ![Requests](https://img.shields.io/badge/Requests-000000?logo=python&logoColor=white) | HTTP wrapper for REST calls |
| robotframework-datadriver | ![DataDriver](https://img.shields.io/badge/DataDriver-000000) | CSV-driven Data-Driven Testing (DDT) |
| Makefile / curl | ![curl](https://img.shields.io/badge/Makefile-000000?logo=curl&logoColor=white) | Orchestration and pre-flight checks |

## Project File Organization

- `tests/` — top-level test documentation and assets
  - [tests/README.md](tests/README.md) — consolidated Robot and test documentation
  - `tests/scenarios/` — human-readable acceptance scenarios
    - [tests/scenarios/e2e_customer_order_flow.md](tests/scenarios/e2e_customer_order_flow.md) — customer order flow scenario
    - [tests/scenarios/e2e_inventory_and_validation_flow.md](tests/scenarios/e2e_inventory_and_validation_flow.md) — inventory and validation scenario
  - `tests/robot/` — Robot Framework project
    - `tests/robot/resources/` — shared Robot keywords and helpers
      - [tests/robot/resources/api.resource](tests/robot/resources/api.resource) — shared API session, CRUD, and assertion keywords
    - `tests/robot/data/` — CSV files consumed by DataDriver
      - [tests/robot/data/customer_order_flow.csv](tests/robot/data/customer_order_flow.csv) — rows for the customer order DDT suite
      - [tests/robot/data/inventory_validation_flow.csv](tests/robot/data/inventory_validation_flow.csv) — rows for the inventory validation DDT suite
    - `tests/robot/suites/` — Robot `.robot` suite files
      - [tests/robot/suites/e2e_customer_order_flow.robot](tests/robot/suites/e2e_customer_order_flow.robot) — customer order workflow suite
      - [tests/robot/suites/e2e_inventory_and_validation_flow.robot](tests/robot/suites/e2e_inventory_and_validation_flow.robot) — inventory validation suite

Other related project files:

- [data/test/](data/test) — deterministic CSV fixtures consumed by `utils/seed_database.py`
- [utils/seed_database.py](utils/seed_database.py) — database seeder used to make API and test runs reproducible
- [Makefile](Makefile) — convenience targets for venv, install, seed, API, and Robot execution
- [req.txt](req.txt) — pinned Python dependencies, including Robot Framework and `pabot`

## Quick Start (install, run, test)

1. Create virtualenv and install dependencies:

```bash
make venv
make install
```

2. Start the API (separate terminal recommended):

```bash
make run-api
```

3. Run Robot suites (in another terminal):

```bash
make test-robot    # requires API running
```

One-shot option (start API, run tests, stop API):

```bash
make test-robot-local
```

Dry-run (validate templates and CSV parsing without HTTP):

```bash
make test-robot-dry
```

Results are written to `tests/robot/results/` (output.xml, log.html, report.html).

## Test Suite Overview

The suites are Data-Driven Tests (DDT) that read rows from CSV files and execute a test template for each row. Important notes:

- CSV files use semicolon delimiters to match `DataDriver` configuration.
- Shared keywords live in `tests/robot/resources/api.resource` and include session setup, create/delete helpers, and deterministic reseed.
- Tests are executed against a running API; set `BASE_URL` to the API base when invoking Robot.

## Troubleshooting

- If you see `ModuleNotFoundError: No module named 'DataDriver'`, your `robot` command is using a different virtual environment.
- Use `.venv/bin/robot` (or activate `.venv`) to run with project dependencies.
- CSV files are semicolon-delimited for DataDriver compatibility.

## Suite overviews

Below is a short description of the two Robot suites and the CSV columns they expect (used by DataDriver):

- **E2E Customer Order Flow** (`tests/robot/suites/e2e_customer_order_flow.robot`)
  - Purpose: create a dedicated category and product, place an order for an existing seeded customer, verify totals and stock changes, then clean up created resources.
  - CSV columns (in order):
    - `${customer_email}` — seeded customer email to use
    - `${category_name}` — category name to create for the test
    - `${category_description}` — category description
    - `${product_name}` — product name to create
    - `${product_description}` — product description
    - `${product_price}` — product price (integer)
    - `${product_stock}` — initial stock quantity (integer)
    - `${order_quantity}` — quantity to order (integer)
    - `${order_date}` — ISO8601 order date/time
    - `${expected_order_status}` — expected order status after create (e.g., Completed)

- **E2E Inventory & Validation Flow** (`tests/robot/suites/e2e_inventory_and_validation_flow.robot`)
  - Purpose: validate referential integrity and inventory rules (e.g., cannot order beyond stock, cannot delete products/customers with dependent records), then clean up.
  - CSV columns (in order):
    - `${category_name}`
    - `${category_description}`
    - `${customer_first_name}`
    - `${customer_last_name}`
    - `${customer_email}`
    - `${customer_phone}`
    - `${product_name}`
    - `${product_description}`
    - `${product_price}`
    - `${product_stock}`
    - `${order_date}`
    - `${order_quantity}`
    - `${overstock_quantity}` — quantity expected to trigger an insufficient-stock conflict

## Keywords reference

This section documents the shared Robot keywords available to suites and what each does. The full implementations live in `tests/robot/resources/api.resource`.

- `Prepare API Session`
  - Runs: `Reset Database To Known State`, `Create Session ${API_ALIAS} ${BASE_URL}`, `API Should Be Healthy`.
  - Use: Suite Setup — ensures tests run from a reproducible base state and have an HTTP session configured.

- `Close API Session`
  - Runs: `Delete All Sessions`.
  - Use: Suite Teardown — closes HTTP sessions.

- `Reset Database To Known State`
  - Invokes the project's seeder via the project `.venv` Python if available, otherwise `python -m utils.seed_database`.
  - Logs seeder output and asserts the seeder exit code is `0`.
  - Use: ensures deterministic demo data (categories, customers, products, orders, order_items) before suite run.

- `API Should Be Healthy`
  - Sends `GET /` and asserts HTTP 200 and the JSON `message` contains `Hello There!!`.
  - Use: quick health-check after session creation.

- `Get Collection By Endpoint`
  - `GET` a collection endpoint (e.g., `/products`) and returns the parsed JSON list after asserting HTTP 200.

- `Find Item By Field`
  - Iterates a collection returned by `Get Collection By Endpoint` and returns the first item where a specified field equals a value. Fails if not found.

- `Get Resource By Id`
  - `GET` a single resource by id (e.g., `/orders/{id}`) and returns parsed JSON after asserting HTTP 200.

- `Create Resource`
  - `POST` a JSON payload to an endpoint and asserts HTTP 201; returns created resource JSON.

- `Create Resource Expecting Conflict`
  - `POST` expecting a conflict (409). Allows non-2xx responses in the request and asserts status `409`.

- `Delete Resource`
  - `DELETE` a resource by id and asserts HTTP 204.

- `Delete Resource Expecting Conflict`
  - `DELETE` allowing non-2xx and asserting `409` when deletion is blocked by referential integrity.

- `Assert Integer Difference`
  - Asserts that `after == before - delta` (used to validate stock quantity decreases).

- `Assert Equal Integer Fields`
  - Asserts that a numeric field in a response body equals an expected integer (used to assert order totals, prices, etc.).

## Example mapping: test → keywords

- `Customer order workflow from CSV` (suite: `e2e_customer_order_flow.robot`)
  - Template `Run Customer Order Workflow` uses `Find Item By Field`, `Create Resource`, `Get Resource By Id`, `Assert Equal Integer Fields`, `Assert Integer Difference`, and cleanup keywords to validate a full order lifecycle.

- `Inventory validation workflow from CSV` (suite: `e2e_inventory_and_validation_flow.robot`)
  - Template `Run Inventory Validation Workflow` creates category/customer/product/order, adds an order item (valid), then attempts to add an oversized order item expecting conflict, verifies delete operations can be blocked by referential integrity, then cleans up.

## Scenarios

The repository contains human-readable scenario definitions that map directly to the Robot DataDriver suites. These files describe goals, preconditions, test data, steps, expected results and postconditions. Keep them updated when you change test flows or CSV fixtures.

- **E2E Scenario 1: Customer Places an Order**
  - File: [tests/scenarios/e2e_customer_order_flow.md](tests/scenarios/e2e_customer_order_flow.md)
  - Purpose: Verify the core API workflow from seeded data through order creation and order item tracking. Preconditions include a running API and seeded demo data. Key checks: API health, presence of seeded customer/product, order and order-item creation, order totals, and stock decrement.

- **E2E Scenario 2: Inventory and Validation Rules**
  - File: [tests/scenarios/e2e_inventory_and_validation_flow.md](tests/scenarios/e2e_inventory_and_validation_flow.md)
  - Purpose: Verify business rules for stock validation, duplicate protection, and delete constraints. Preconditions include a running API and seeded demo data. Key checks: category/customer/product/order creation, valid and oversized order-item handling (expect 409), and deletion constraints (expect 409).

Tip: The Robot suites implement these scenarios as DataDriver-driven test templates. Use the scenario files as readable acceptance criteria when updating CSV fixtures or test templates.
