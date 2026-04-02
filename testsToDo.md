# Tests To Do

Manual test plan for all API models.

## Navigation

- [Setup](#setup)
- [Reusable Data (Use First)](#reusable-data-use-first)
- [Health Check Test](#health-check-test)
- [Category Tests](#category-tests)
- [Product Tests](#product-tests)
- [Customer Tests](#customer-tests)
- [Order Tests](#order-tests)
- [Order Item Tests (Business Rules)](#order-item-tests-business-rules)
- [Status Code Coverage By Endpoint](#status-code-coverage-by-endpoint)

## Setup

```bash
source .venv/bin/activate
uvicorn main:app --reload
```

- Base URL: `http://127.0.0.1:8000`
- Docs: `http://127.0.0.1:8000/docs`

## Reusable Data (Use First)

### Category Create Body

Endpoint: `POST http://127.0.0.1:8000/categories`

```json
{
  "name": "Electronics",
  "description": "Devices and accessories"
}
```

### Product Create Body

Endpoint: `POST http://127.0.0.1:8000/products`

```json
{
  "name": "Wireless Mouse",
  "description": "2.4GHz USB mouse",
  "price": 25,
  "stock_quantity": 20,
  "category_id": 1
}
```

### Customer Create Body

Endpoint: `POST http://127.0.0.1:8000/customers`

```json
{
  "first_name": "Fahd",
  "last_name": "K",
  "email": "fahd@example.com",
  "phone": "+212600000000"
}
```

### Order Create Body

Endpoint: `POST http://127.0.0.1:8000/orders`

```json
{
  "customer_id": 1,
  "order_date": "2026-04-02T10:00:00Z",
  "total_amount": 0,
  "status": "Pending"
}
```

### Order Item Create Body

Endpoint: `POST http://127.0.0.1:8000/order-items`

```json
{
  "order_id": 1,
  "product_id": 1,
  "quantity": 2,
  "price": 25
}
```

## Health Check Test

- [x] `GET http://127.0.0.1:8000/`
  - Expected output: status `200`, JSON contains `Hello There!!`
  - Expected behavior: API is reachable and running

## Category Tests

| Done | Test | Endpoint | Request Body | Status Code | Expected Behavior |
|---|---|---|---|---|---|
| [[x]] | Create category | `POST /categories` | <pre><code class="language-json">{<br>  "name": "Electronics",<br>  "description": "Devices and accessories"<br>}</code></pre> | `201` | Category is persisted and can be fetched later |
| [x] | Create duplicate category | `POST /categories` | <pre><code class="language-json">{<br>  "name": "Electronics",<br>  "description": "Devices and accessories"<br>}</code></pre> | `409` | Duplicate unique name is rejected |
| [x] | List categories with pagination | `GET /categories?skip=0&limit=1` | `N/A` | `200` | Pagination parameters are respected |
| [x] | List categories with invalid pagination | `GET /categories?skip=-1&limit=10` | `N/A` | `400` | Invalid pagination is rejected |
| [x] | Get category by valid ID | `GET /categories/{category_id}` | `N/A` | `200` | Correct category is returned |
| [x] | Get category by invalid ID | `GET /categories/999999` | `N/A` | `404` | Not found response for missing ID |
| [x] | Update category | `PUT /categories/{category_id}` | <pre><code class="language-json">{<br>  "name": "Electronics-Updated",<br>  "description": "Updated description"<br>}</code></pre> | `200` | Category values are modified |
| [x] | Delete category with referenced products | `DELETE /categories/{category_id}` | `N/A` | `409` | Protected from deletion when linked products exist |
| [x] | Delete category successfully | `DELETE /categories/{category_id}` | `N/A` | `204` | Precondition: no linked products; subsequent `GET` returns `404` |

## Product Tests

| Done | Test | Endpoint | Request Body | Status Code | Expected Behavior |
|---|---|---|---|---|---|
| [ ] | Create product | `POST /products` | <pre><code class="language-json">{<br>  "name": "Wireless Mouse",<br>  "description": "2.4GHz USB mouse",<br>  "price": 25,<br>  "stock_quantity": 20,<br>  "category_id": 1<br>}</code></pre> | `201` | Product is persisted |
| [ ] | Create product with invalid name | `POST /products` | <pre><code class="language-json">{<br>  "name": "a",<br>  "description": "2.4GHz USB mouse",<br>  "price": 25,<br>  "stock_quantity": 20,<br>  "category_id": 1<br>}</code></pre> | `400` or `422` | Model validation blocks invalid name |
| [ ] | Create product with invalid category | `POST /products` | <pre><code class="language-json">{<br>  "name": "Wireless Mouse",<br>  "description": "2.4GHz USB mouse",<br>  "price": 25,<br>  "stock_quantity": 20,<br>  "category_id": 999999<br>}</code></pre> | `409` | FK integrity is enforced |
| [ ] | List products with pagination | `GET /products?skip=0&limit=2` | `N/A` | `200` | Returns paginated products |
| [ ] | Get product by valid ID | `GET /products/{product_id}` | `N/A` | `200` | Returns exact product |
| [ ] | Update product | `PUT /products/{product_id}` | <pre><code class="language-json">{<br>  "name": "Wireless Mouse Pro",<br>  "description": "2.4GHz USB mouse",<br>  "price": 30,<br>  "stock_quantity": 18,<br>  "category_id": 1<br>}</code></pre> | `200` | Price and stock are updated |
| [ ] | Delete product referenced by order items | `DELETE /products/{product_id}` | `N/A` | `409` | Referenced product cannot be deleted |
| [ ] | Delete product successfully | `DELETE /products/{product_id}` | `N/A` | `204` | Precondition: no related order items; subsequent `GET` returns `404` |

## Customer Tests

| Done | Test | Endpoint | Request Body | Status Code | Expected Behavior |
|---|---|---|---|---|---|
| [ ] | Create customer | `POST /customers` | <pre><code class="language-json">{<br>  "first_name": "Fahd",<br>  "last_name": "K",<br>  "email": "fahd@example.com",<br>  "phone": "+212600000000"<br>}</code></pre> | `201` | Customer is persisted |
| [ ] | Create customer with duplicate email | `POST /customers` | <pre><code class="language-json">{<br>  "first_name": "Fahd",<br>  "last_name": "K",<br>  "email": "fahd@example.com",<br>  "phone": "+212600000000"<br>}</code></pre> | `409` | Unique email constraint enforced |
| [ ] | Get customer by valid ID | `GET /customers/{customer_id}` | `N/A` | `200` | Customer record is returned |
| [ ] | Update customer phone | `PUT /customers/{customer_id}` | <pre><code class="language-json">{<br>  "first_name": "Fahd",<br>  "last_name": "K",<br>  "email": "fahd@example.com",<br>  "phone": "+212611111111"<br>}</code></pre> | `200` | Phone number is updated |
| [ ] | Delete customer with orders | `DELETE /customers/{customer_id}` | `N/A` | `409` | Customer cannot be deleted when linked orders exist |
| [ ] | Delete customer successfully | `DELETE /customers/{customer_id}` | `N/A` | `204` | Precondition: no related orders; subsequent `GET` returns `404` |

## Order Tests

| Done | Test | Endpoint | Request Body | Status Code | Expected Behavior |
|---|---|---|---|---|---|
| [ ] | Create order | `POST /orders` | <pre><code class="language-json">{<br>  "customer_id": 1,<br>  "order_date": "2026-04-02T10:00:00Z",<br>  "total_amount": 0,<br>  "status": "Pending"<br>}</code></pre> | `201` | Order is created for the customer |
| [ ] | Create order with invalid customer | `POST /orders` | <pre><code class="language-json">{<br>  "customer_id": 999999,<br>  "order_date": "2026-04-02T10:00:00Z",<br>  "total_amount": 0,<br>  "status": "Pending"<br>}</code></pre> | `409` | FK integrity is enforced |
| [ ] | Get order by valid ID | `GET /orders/{order_id}` | `N/A` | `200` | Order is returned |
| [ ] | Update order status | `PUT /orders/{order_id}` | <pre><code class="language-json">{<br>  "customer_id": 1,<br>  "order_date": "2026-04-02T10:00:00Z",<br>  "total_amount": 9999,<br>  "status": "Completed"<br>}</code></pre> | `200` | Status updates; total remains computed from order items |
| [ ] | Delete order with order items | `DELETE /orders/{order_id}` | `N/A` | `409` | Delete is blocked when linked items exist |
| [ ] | Delete order successfully | `DELETE /orders/{order_id}` | `N/A` | `204` | Precondition: all related order items deleted; subsequent `GET` returns `404` |

## Order Item Tests (Business Rules)

| Done | Test | Endpoint | Request Body | Status Code | Expected Behavior |
|---|---|---|---|---|---|
| [ ] | Create order item with enough stock | `POST /order-items` | <pre><code class="language-json">{<br>  "order_id": 1,<br>  "product_id": 1,<br>  "quantity": 2,<br>  "price": 25<br>}</code></pre> | `201` | Product stock decreases and order total increases automatically |
| [ ] | Create order item with insufficient stock | `POST /order-items` | <pre><code class="language-json">{<br>  "order_id": 1,<br>  "product_id": 1,<br>  "quantity": 999,<br>  "price": 25<br>}</code></pre> | `409` | No stock change and no order item created |
| [ ] | Get order item by valid ID | `GET /order-items/{order_item_id}` | `N/A` | `200` | Order item is returned |
| [ ] | Update order item quantity within stock | `PUT /order-items/{order_item_id}` | <pre><code class="language-json">{<br>  "order_id": 1,<br>  "product_id": 1,<br>  "quantity": 3,<br>  "price": 25<br>}</code></pre> | `200` | Stock reconciled and order total recalculated |
| [ ] | Update order item with insufficient stock | `PUT /order-items/{order_item_id}` | <pre><code class="language-json">{<br>  "order_id": 1,<br>  "product_id": 1,<br>  "quantity": 999,<br>  "price": 25<br>}</code></pre> | `409` | Update rejected and stock remains consistent |
| [ ] | Delete order item | `DELETE /order-items/{order_item_id}` | `N/A` | `204` | Stock restored and order total recalculated downward |

## Status Code Coverage By Endpoint

Use this section to ensure each method is validated against all status codes it can return.

### Categories

| Done | Endpoint | Status Code | Scenario |
|---|---|---|---|
| [ ] | `POST /categories` | `201` | Valid body |
| [ ] | `POST /categories` | `400` | Invalid body (for example missing required fields) |
| [ ] | `POST /categories` | `409` | Duplicate name |
| [ ] | `POST /categories` | `500` | Simulate DB/server failure |
| [ ] | `GET /categories` | `200` | Valid request |
| [ ] | `GET /categories` | `400` | Invalid pagination (`skip=-1` or `limit=0`) |
| [ ] | `GET /categories` | `500` | Simulate DB/server failure |
| [ ] | `GET /categories/{id}` | `200` | Existing ID |
| [ ] | `GET /categories/{id}` | `404` | Non-existing ID |
| [ ] | `GET /categories/{id}` | `500` | Simulate DB/server failure |
| [ ] | `PUT /categories/{id}` | `200` | Existing ID and valid body |
| [ ] | `PUT /categories/{id}` | `404` | Non-existing ID |
| [ ] | `PUT /categories/{id}` | `400` | Invalid body |
| [ ] | `PUT /categories/{id}` | `409` | Conflict (for example duplicate unique name) |
| [ ] | `PUT /categories/{id}` | `500` | Simulate DB/server failure |
| [ ] | `DELETE /categories/{id}` | `204` | Deletable record |
| [ ] | `DELETE /categories/{id}` | `404` | Non-existing ID |
| [ ] | `DELETE /categories/{id}` | `409` | Record has related products |
| [ ] | `DELETE /categories/{id}` | `500` | Simulate DB/server failure |

### Products

| Done | Endpoint | Status Code | Scenario |
|---|---|---|---|
| [ ] | `POST /products` | `201` | Valid body |
| [ ] | `POST /products` | `400` or `422` | Invalid body |
| [ ] | `POST /products` | `409` | Invalid FK/conflict |
| [ ] | `POST /products` | `500` | Simulate DB/server failure |
| [ ] | `GET /products` | `200` | Valid request |
| [ ] | `GET /products` | `400` | Invalid pagination |
| [ ] | `GET /products` | `500` | Simulate DB/server failure |
| [ ] | `GET /products/{id}` | `200` | Existing ID |
| [ ] | `GET /products/{id}` | `404` | Non-existing ID |
| [ ] | `GET /products/{id}` | `500` | Simulate DB/server failure |
| [ ] | `PUT /products/{id}` | `200` | Existing ID and valid body |
| [ ] | `PUT /products/{id}` | `404` | Non-existing ID |
| [ ] | `PUT /products/{id}` | `400` or `422` | Invalid body |
| [ ] | `PUT /products/{id}` | `409` | Conflict/FK issue |
| [ ] | `PUT /products/{id}` | `500` | Simulate DB/server failure |
| [ ] | `DELETE /products/{id}` | `204` | Deletable record |
| [ ] | `DELETE /products/{id}` | `404` | Non-existing ID |
| [ ] | `DELETE /products/{id}` | `409` | Record linked to order items |
| [ ] | `DELETE /products/{id}` | `500` | Simulate DB/server failure |

### Customers

| Done | Endpoint | Status Code | Scenario |
|---|---|---|---|
| [ ] | `POST /customers` | `201` | Valid body |
| [ ] | `POST /customers` | `400` or `422` | Invalid body |
| [ ] | `POST /customers` | `409` | Duplicate email |
| [ ] | `POST /customers` | `500` | Simulate DB/server failure |
| [ ] | `GET /customers` | `200` | Valid request |
| [ ] | `GET /customers` | `400` | Invalid pagination |
| [ ] | `GET /customers` | `500` | Simulate DB/server failure |
| [ ] | `GET /customers/{id}` | `200` | Existing ID |
| [ ] | `GET /customers/{id}` | `404` | Non-existing ID |
| [ ] | `GET /customers/{id}` | `500` | Simulate DB/server failure |
| [ ] | `PUT /customers/{id}` | `200` | Existing ID and valid body |
| [ ] | `PUT /customers/{id}` | `404` | Non-existing ID |
| [ ] | `PUT /customers/{id}` | `400` or `422` | Invalid body |
| [ ] | `PUT /customers/{id}` | `409` | Conflict (for example duplicate email) |
| [ ] | `PUT /customers/{id}` | `500` | Simulate DB/server failure |
| [ ] | `DELETE /customers/{id}` | `204` | Deletable record |
| [ ] | `DELETE /customers/{id}` | `404` | Non-existing ID |
| [ ] | `DELETE /customers/{id}` | `409` | Record linked to orders |
| [ ] | `DELETE /customers/{id}` | `500` | Simulate DB/server failure |

### Orders

| Done | Endpoint | Status Code | Scenario |
|---|---|---|---|
| [ ] | `POST /orders` | `201` | Valid body |
| [ ] | `POST /orders` | `400` or `422` | Invalid body |
| [ ] | `POST /orders` | `409` | Invalid customer FK/conflict |
| [ ] | `POST /orders` | `500` | Simulate DB/server failure |
| [ ] | `GET /orders` | `200` | Valid request |
| [ ] | `GET /orders` | `400` | Invalid pagination |
| [ ] | `GET /orders` | `500` | Simulate DB/server failure |
| [ ] | `GET /orders/{id}` | `200` | Existing ID |
| [ ] | `GET /orders/{id}` | `404` | Non-existing ID |
| [ ] | `GET /orders/{id}` | `500` | Simulate DB/server failure |
| [ ] | `PUT /orders/{id}` | `200` | Existing ID and valid body |
| [ ] | `PUT /orders/{id}` | `404` | Non-existing ID |
| [ ] | `PUT /orders/{id}` | `400` or `422` | Invalid body |
| [ ] | `PUT /orders/{id}` | `409` | Conflict/FK issue |
| [ ] | `PUT /orders/{id}` | `500` | Simulate DB/server failure |
| [ ] | `DELETE /orders/{id}` | `204` | Deletable record |
| [ ] | `DELETE /orders/{id}` | `404` | Non-existing ID |
| [ ] | `DELETE /orders/{id}` | `409` | Record linked to order items |
| [ ] | `DELETE /orders/{id}` | `500` | Simulate DB/server failure |

### Order Items

| Done | Endpoint | Status Code | Scenario |
|---|---|---|---|
| [ ] | `POST /order-items` | `201` | Valid body with enough stock |
| [ ] | `POST /order-items` | `400` or `422` | Invalid body |
| [ ] | `POST /order-items` | `404` | Missing order or product |
| [ ] | `POST /order-items` | `409` | Insufficient stock or integrity conflict |
| [ ] | `POST /order-items` | `500` | Simulate DB/server failure |
| [ ] | `GET /order-items` | `200` | Valid request |
| [ ] | `GET /order-items` | `400` | Invalid pagination |
| [ ] | `GET /order-items` | `500` | Simulate DB/server failure |
| [ ] | `GET /order-items/{id}` | `200` | Existing ID |
| [ ] | `GET /order-items/{id}` | `404` | Non-existing ID |
| [ ] | `GET /order-items/{id}` | `500` | Simulate DB/server failure |
| [ ] | `PUT /order-items/{id}` | `200` | Valid body with enough stock |
| [ ] | `PUT /order-items/{id}` | `400` or `422` | Invalid body |
| [ ] | `PUT /order-items/{id}` | `404` | Missing target order item or product |
| [ ] | `PUT /order-items/{id}` | `409` | Insufficient stock/conflict |
| [ ] | `PUT /order-items/{id}` | `500` | Simulate DB/server failure |
| [ ] | `DELETE /order-items/{id}` | `204` | Deletable record |
| [ ] | `DELETE /order-items/{id}` | `404` | Non-existing ID |
| [ ] | `DELETE /order-items/{id}` | `409` | Conflict |
| [ ] | `DELETE /order-items/{id}` | `500` | Simulate DB/server failure |
