# E2E Scenario 1: Customer Places an Order

## Goal
Verify the core API workflow from seeded data through order creation and order item tracking.

## Preconditions
- The API is running at `http://127.0.0.1:8000`.
- The database has been seeded, or starts empty so the app seeds automatically on startup.
- The initial seed data includes at least one customer, one category, and one product with enough stock.

## Test Data
- DataDriver source: [tests/robot/data/customer_order_flow.csv](../robot/data/customer_order_flow.csv)
- Dynamic placeholders used by the suite:
	- `${customer_email}`
	- `${category_name}`
	- `${category_description}`
	- `${product_name}`
	- `${product_description}`
	- `${product_price}`
	- `${product_stock}`
	- `${order_quantity}`
	- `${order_date}`
	- `${expected_order_status}`

## Steps
1. Send `GET /` and confirm the API responds with status `200`.
2. Locate the seeded customer using `${customer_email}`.
3. Create a category using `${category_name}` and `${category_description}`.
4. Create a product using `${product_name}`, `${product_description}`, `${product_price}`, `${product_stock}`, and the created category id.
5. Create an order for the selected customer using `${order_date}` and `${expected_order_status}`.
6. Create an order item for that order using `${order_quantity}` and the product price.
7. Fetch the order with `GET /orders/{order_id}`.
8. Fetch the order item with `GET /order-items/{order_item_id}`.
9. Fetch the product with `GET /products/{product_id}` and confirm stock was reduced by `${order_quantity}`.

## Expected Results
- The health check returns `200`.
- The customer selected by `${customer_email}` is used in the flow.
- The category and product are created successfully with `201`.
- The order is created successfully with status `201`.
- The order item is created successfully with status `201`.
- The order total reflects `${product_price} * ${order_quantity}`.
- The product stock decreases by `${order_quantity}`.
- The order and order item can both be retrieved after creation.

## Postconditions
- The database contains a new order linked to the selected customer.
- The database contains a new order item linked to the order and product.
