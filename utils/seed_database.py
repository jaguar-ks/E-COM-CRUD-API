"""Seed the local SQLite database with reproducible demo data.

Run from the project root:

    python -m utils.seed_database

The script recreates sample categories, customers, products, orders, and order
items. By default it clears existing rows first so repeated runs stay
deterministic.
"""

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path

from sqlmodel import SQLModel, Session, delete

from db import engine
from models import Category, Customer, Order, OrderItem, OrderStatus, Product

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "test"
CATEGORY_FILE = DATA_DIR / "categories.csv"
CUSTOMER_FILE = DATA_DIR / "customers.csv"
PRODUCT_FILE = DATA_DIR / "products.csv"
ORDER_FILE = DATA_DIR / "orders.csv"
ORDER_ITEM_FILE = DATA_DIR / "order_items.csv"


def load_csv_rows(csv_path: Path) -> list[dict[str, str]]:
    """Load rows from a CSV fixture file."""
    if not csv_path.exists():
        raise FileNotFoundError(f"Seed data file not found: {csv_path}")

    with csv_path.open(newline="", encoding="utf-8") as file_handle:
        reader = csv.DictReader(file_handle)
        return [
            {key: (value.strip() if value is not None else "") for key, value in row.items()}
            for row in reader
        ]


def clear_existing_data(session: Session) -> None:
    """Remove existing rows so the seed remains deterministic."""
    for model in (OrderItem, Order, Product, Customer, Category):
        session.exec(delete(model))
    session.commit()


def seed_categories(session: Session, category_rows: list[dict[str, str]]) -> dict[str, Category]:
    categories: list[Category] = []
    for category_data in category_rows:
        category = Category(
            name=category_data["name"],
            description=category_data["description"] or None,
        )
        session.add(category)
        categories.append(category)

    session.commit()
    for category in categories:
        session.refresh(category)

    return {category.name: category for category in categories}


def seed_customers(session: Session, customer_rows: list[dict[str, str]]) -> dict[str, Customer]:
    customers: list[Customer] = []
    for customer_data in customer_rows:
        customer = Customer(
            first_name=customer_data["first_name"],
            last_name=customer_data["last_name"],
            email=customer_data["email"],
            phone=customer_data["phone"] or None,
        )
        session.add(customer)
        customers.append(customer)

    session.commit()
    for customer in customers:
        session.refresh(customer)

    return {customer.email: customer for customer in customers}


def seed_products(
    session: Session,
    categories: dict[str, Category],
    product_rows: list[dict[str, str]],
) -> dict[str, Product]:
    products: list[Product] = []
    for product_data in product_rows:
        category = categories[product_data["category_ref"]]
        product = Product(
            name=product_data["name"],
            description=product_data["description"] or None,
            price=int(product_data["price"]),
            stock_quantity=int(product_data["stock_quantity"]),
            category_id=category.id,
        )
        session.add(product)
        products.append(product)

    session.commit()
    for product in products:
        session.refresh(product)

    return {product.name: product for product in products}


def seed_orders_and_items(
    session: Session,
    customers: dict[str, Customer],
    products: dict[str, Product],
    order_rows: list[dict[str, str]],
    order_item_rows: list[dict[str, str]],
) -> None:
    orders: dict[str, Order] = {}
    for order_data in order_rows:
        customer = customers[order_data["customer_ref"]]
        order = Order(
            customer_id=customer.id,
            order_date=datetime.now(timezone.utc),
            total_amount=0,
            status=OrderStatus(order_data["status"]),
        )
        session.add(order)
        session.flush()
        orders[order_data["ref"]] = order

    for order_data in order_rows:
        order = orders[order_data["ref"]]
        order_total = 0
        for item_data in [row for row in order_item_rows if row["order_ref"] == order_data["ref"]]:
            product = products[item_data["product_ref"]]
            quantity = int(item_data["quantity"])

            if product.stock_quantity < quantity:
                raise ValueError(
                    f"Insufficient stock for {product.name}: "
                    f"available={product.stock_quantity}, requested={quantity}"
                )

            product.stock_quantity -= quantity
            session.add(product)

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                price=product.price,
            )
            session.add(order_item)
            order_total += quantity * product.price

        order.total_amount = order_total
        session.add(order)

    session.commit()


def seed_database(reset_existing: bool = True) -> None:
    """Create tables and populate them with demo data."""
    SQLModel.metadata.create_all(engine)
    category_rows = load_csv_rows(CATEGORY_FILE)
    customer_rows = load_csv_rows(CUSTOMER_FILE)
    product_rows = load_csv_rows(PRODUCT_FILE)
    order_rows = load_csv_rows(ORDER_FILE)
    order_item_rows = load_csv_rows(ORDER_ITEM_FILE)

    with Session(engine) as session:
        if reset_existing:
            clear_existing_data(session)

        categories = seed_categories(session, category_rows)
        customers = seed_customers(session, customer_rows)
        products = seed_products(session, categories, product_rows)
        seed_orders_and_items(
            session,
            customers,
            products,
            order_rows,
            order_item_rows,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed the local database with demo data.")
    parser.add_argument(
        "--keep-existing",
        action="store_true",
        help="Keep existing rows instead of clearing the database before seeding.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    seed_database(reset_existing=not args.keep_existing)
    print("Database seeded successfully.")


if __name__ == "__main__":
    main()
