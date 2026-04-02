from .product import Product, ProductCreate
from .category import Category, CategoryCreate
from .customer import Customer, CustomerCreate
from .order import Order, OrderCreate, OrderStatus
from .order_item import OrderItem, OrderItemCreate

Product.model_rebuild()
Category.model_rebuild()
Customer.model_rebuild()
Order.model_rebuild()
OrderItem.model_rebuild()
