from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel

import models
from db import engine
from routes import (
    categories_router,
    customers_router,
    order_items_router,
    orders_router,
    products_router,
)


@asynccontextmanager
async def create_tables(app: FastAPI):
    SQLModel.metadata.create_all(engine)
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
