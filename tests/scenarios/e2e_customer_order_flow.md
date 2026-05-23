# E2E Scenario 1: Customer Places an Order

## Goal
Verify the core API workflow from seeded data through order creation and order item tracking.

## Preconditions
- The API is running at `http://127.0.0.1:8000`.
- The database has been seeded, or starts empty so the app seeds automatically on startup.
- The initial seed data includes at least one customer, one category, and one product with enough stock.

## Test Data
- Customer: `ava.johnson@example.com`
- Product: `Wireless Headphones`
- Product quantity to order: `1`

## Steps
1. Send `GET /` and confirm the API responds with status `200`.
2. Send `GET /customers` and confirm the seeded customer is present.
3. Send `GET /products` and confirm the seeded product is present.
4. Create an order with the seeded customer using `POST /orders`.
5. Create an order item for that order using `POST /order-items`.
6. Fetch the order with `GET /orders/{order_id}`.
7. Fetch the order item with `GET /order-items/{order_item_id}`.
8. Fetch the product with `GET /products/{product_id}` and confirm stock was reduced.

## Expected Results
- The health check returns `200`.
- The customer and product are returned from the list endpoints.
- The order is created successfully with status `201`.
- The order item is created successfully with status `201`.
- The order total reflects the order item amount.
- The product stock decreases by the ordered quantity.
- The order and order item can both be retrieved after creation.

## Postconditions
- The database contains a new order linked to the selected customer.
- The database contains a new order item linked to the order and product.
