# E2E Scenario 2: Inventory and Validation Rules

## Goal
Verify business rules for stock validation, duplicate protection, and delete constraints.

## Preconditions
- The API is running at `http://127.0.0.1:8000`.
- The database is seeded with the demo data.
- At least one category, customer, product, order, and order item already exist.

## Test Data
- DataDriver source: [tests/robot/data/inventory_validation_flow.csv](../robot/data/inventory_validation_flow.csv)
- Dynamic placeholders used by the suite:
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
	- `${overstock_quantity}`

## Steps
1. Create a new category using `${category_name}` and `${category_description}`.
2. Create a new customer using `${customer_first_name}`, `${customer_last_name}`, `${customer_email}`, and `${customer_phone}`.
3. Create a new product linked to the category using `${product_name}`, `${product_description}`, `${product_price}`, and `${product_stock}`.
4. Create a valid order for the customer using `${order_date}`.
5. Create an order item that uses available product stock with `${order_quantity}`.
6. Attempt to create another order item for the same product with `${overstock_quantity}`.
7. Attempt to delete a product that is referenced by an order item.
8. Attempt to delete a customer that still has an order.

## Expected Results
- Category creation returns `201`.
- Customer creation returns `201`.
- Product creation returns `201`.
- Order creation returns `201`.
- The first order item creation returns `201` and reduces product stock by `${order_quantity}`.
- The oversized order item request using `${overstock_quantity}` is rejected with `409`.
- The referenced product delete request is rejected with `409`.
- The customer delete request is rejected with `409`.

## Postconditions
- Business rules remain enforced after the workflow runs.
- Stock levels and referential integrity stay consistent.
