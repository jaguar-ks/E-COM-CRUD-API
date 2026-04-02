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

- [ ] `GET http://127.0.0.1:8000/`
  - Expected output: status `200`, JSON contains `Hello There!!`
  - Expected behavior: API is reachable and running

## Category Tests

- [ ] Create category
  - Endpoint: `POST /categories`
  - Body: Category Create Body
  - Expected output: `201`, returned category with `id`
  - Expected behavior: category is persisted and can be fetched later

- [ ] Create duplicate category
  - Endpoint: `POST /categories`
  - Body: same category name
  - Expected output: `409`
  - Expected behavior: duplicate unique name is rejected

- [ ] List categories with pagination
  - Endpoint: `GET /categories?skip=0&limit=1`
  - Expected output: `200`, max one item
  - Expected behavior: pagination parameters are respected

- [ ] List categories with invalid pagination
  - Endpoint: `GET /categories?skip=-1&limit=10`
  - Expected output: `400`
  - Expected behavior: invalid pagination is rejected

- [ ] Get category by valid ID
  - Endpoint: `GET /categories/{category_id}`
  - Expected output: `200`, category JSON
  - Expected behavior: correct category is returned

- [ ] Get category by invalid ID
  - Endpoint: `GET /categories/999999`
  - Expected output: `404`
  - Expected behavior: not found response for missing ID

- [ ] Update category
  - Endpoint: `PUT /categories/{category_id}`
  - Body:

```json
{
  "name": "Electronics-Updated",
  "description": "Updated description"
}
```

  - Expected output: `200`, updated category
  - Expected behavior: category values are modified

- [ ] Delete category with referenced products
  - Endpoint: `DELETE /categories/{category_id}`
  - Expected output: `409`
  - Expected behavior: protected from deletion when linked products exist

## Product Tests

- [ ] Create product
  - Endpoint: `POST /products`
  - Body: Product Create Body
  - Expected output: `201`, returned product with `id`
  - Expected behavior: product is persisted

- [ ] Create product with invalid name
  - Endpoint: `POST /products`
  - Body: same as product create but `name: "a"`
  - Expected output: validation error (`400` or `422`)
  - Expected behavior: model validation blocks invalid name

- [ ] Create product with invalid category
  - Endpoint: `POST /products`
  - Body: category_id not existing
  - Expected output: `409`
  - Expected behavior: FK integrity is enforced

- [ ] List products with pagination
  - Endpoint: `GET /products?skip=0&limit=2`
  - Expected output: `200`
  - Expected behavior: returns paginated products

- [ ] Get product by valid ID
  - Endpoint: `GET /products/{product_id}`
  - Expected output: `200`
  - Expected behavior: returns exact product

- [ ] Update product
  - Endpoint: `PUT /products/{product_id}`
  - Body:

```json
{
  "name": "Wireless Mouse Pro",
  "description": "2.4GHz USB mouse",
  "price": 30,
  "stock_quantity": 18,
  "category_id": 1
}
```

  - Expected output: `200`
  - Expected behavior: price and stock are updated

- [ ] Delete product referenced by order items
  - Endpoint: `DELETE /products/{product_id}`
  - Expected output: `409`
  - Expected behavior: referenced product cannot be deleted

## Customer Tests

- [ ] Create customer
  - Endpoint: `POST /customers`
  - Body: Customer Create Body
  - Expected output: `201`, returned customer with `id`
  - Expected behavior: customer is persisted

- [ ] Create customer with duplicate email
  - Endpoint: `POST /customers`
  - Body: same email
  - Expected output: `409`
  - Expected behavior: unique email constraint enforced

- [ ] Get customer by valid ID
  - Endpoint: `GET /customers/{customer_id}`
  - Expected output: `200`
  - Expected behavior: customer record is returned

- [ ] Update customer phone
  - Endpoint: `PUT /customers/{customer_id}`
  - Body:

```json
{
  "first_name": "Fahd",
  "last_name": "K",
  "email": "fahd@example.com",
  "phone": "+212611111111"
}
```

  - Expected output: `200`
  - Expected behavior: phone number is updated

- [ ] Delete customer with orders
  - Endpoint: `DELETE /customers/{customer_id}`
  - Expected output: `409`
  - Expected behavior: customer cannot be deleted when linked orders exist

## Order Tests

- [ ] Create order
  - Endpoint: `POST /orders`
  - Body: Order Create Body
  - Expected output: `201`, returned order with `id`
  - Expected behavior: order is created for the customer

- [ ] Create order with invalid customer
  - Endpoint: `POST /orders`
  - Body: customer_id not existing
  - Expected output: `409`
  - Expected behavior: FK integrity is enforced

- [ ] Get order by valid ID
  - Endpoint: `GET /orders/{order_id}`
  - Expected output: `200`
  - Expected behavior: order is returned

- [ ] Update order status
  - Endpoint: `PUT /orders/{order_id}`
  - Body:

```json
{
  "customer_id": 1,
  "order_date": "2026-04-02T10:00:00Z",
  "total_amount": 9999,
  "status": "Completed"
}
```

  - Expected output: `200`
  - Expected behavior: status updates, total remains computed from order items

- [ ] Delete order with order items
  - Endpoint: `DELETE /orders/{order_id}`
  - Expected output: `409`
  - Expected behavior: order delete is blocked when linked items exist

## Order Item Tests (Business Rules)

- [ ] Create order item with enough stock
  - Endpoint: `POST /order-items`
  - Body: Order Item Create Body
  - Expected output: `201`
  - Expected behavior: product stock decreases and order total increases automatically

- [ ] Create order item with insufficient stock
  - Endpoint: `POST /order-items`
  - Body: quantity greater than current stock
  - Expected output: `409`
  - Expected behavior: no stock change and no order item created

- [ ] Get order item by valid ID
  - Endpoint: `GET /order-items/{order_item_id}`
  - Expected output: `200`
  - Expected behavior: order item is returned

- [ ] Update order item quantity within stock
  - Endpoint: `PUT /order-items/{order_item_id}`
  - Body:

```json
{
  "order_id": 1,
  "product_id": 1,
  "quantity": 3,
  "price": 25
}
```

  - Expected output: `200`
  - Expected behavior: stock is reconciled and order total is recalculated

- [ ] Update order item with insufficient stock
  - Endpoint: `PUT /order-items/{order_item_id}`
  - Body: quantity greater than stock
  - Expected output: `409`
  - Expected behavior: update is rejected and stock remains consistent

- [ ] Delete order item
  - Endpoint: `DELETE /order-items/{order_item_id}`
  - Expected output: `204`
  - Expected behavior: stock is restored and order total is recalculated downward
