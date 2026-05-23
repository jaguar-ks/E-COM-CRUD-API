from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel, Session, select

import models
from utils.db import engine
from models import Category, Customer, Order, OrderItem, Product
from utils.seed_database import seed_database
from routes import (
    categories_router,
    customers_router,
    order_items_router,
    orders_router,
    products_router,
)


def database_is_empty(session: Session) -> bool:
    """Return True when the core tables do not contain any rows yet."""
    tables = (Category, Customer, Product, Order, OrderItem)
    return all(session.exec(select(table).limit(1)).first() is None for table in tables)


@asynccontextmanager
async def create_tables(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        if database_is_empty(session):
            seed_database(reset_existing=False)
    yield


app = FastAPI(
    title="E-COM CRUD API",
    version="1.0.0",
    description="CRUD API for products, categories, customers, orders, and order items.",
    lifespan=create_tables,
)


@app.get("/")
async def main():
    """Health-check endpoint for verifying the API is running."""
    return {"message": "Hello There!!"}


app.include_router(products_router)
app.include_router(categories_router)
app.include_router(customers_router)
app.include_router(orders_router)
app.include_router(order_items_router)
